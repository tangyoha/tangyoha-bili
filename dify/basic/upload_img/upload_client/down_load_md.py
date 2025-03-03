import aiohttp
import asyncio
import os
import ssl
import re
import sys
import argparse
from urllib.parse import urlparse

# Function to upload a single file using aiohttp
async def upload_file(session, file_path, api_url):
    mpwriter = aiohttp.MultipartWriter('form-data')
    with open(file_path, 'rb') as f:
        mpwriter.append(f, {
            'Content-Disposition': f'form-data; name="files"; filename="{os.path.basename(file_path)}"'
        })
        for _ in range(3):  # Try up to 3 times
            async with session.post(api_url, data=mpwriter) as response:
                result = await response.text()
                try:
                    code = re.search(r'"code":(-?\d+)', result)
                    if code and code.group(1) == '-1':
                        await asyncio.sleep(1)
                    else:
                        return result
                except Exception as e:
                    print(f"{result} {e}")
        raise Exception(f'Upload failed {file_path} after 3 attempts')

# Function to download a single image
async def download_image(session, image_url, save_path):
    async with session.get(image_url) as response:
        if response.status == 200:
            with open(save_path, 'wb') as f:
                f.write(await response.read())
            return save_path
    return None

# Function to process a single markdown file
async def process_markdown_file(session, root_path, md_file_path, mode, api_url):
    with open(md_file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    markdown_image_regex = r'!\[.*?\]\((.*?)\)'
    html_image_regex = r'<img\s.*?src=["\'](.*?)["\'].*?>'
    link_regex = r'\[.*?\]\((.*?)\)'
    image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp')
    
    markdown_images = re.findall(markdown_image_regex, content)
    html_images = re.findall(html_image_regex, content)
    all_links = re.findall(link_regex, content)
    all_images = markdown_images + html_images
    
    print(f"Processing file: {md_file_path}")

    if mode == 'post':
        for image_path in all_images:
            if image_path.lower().endswith(image_extensions) and not image_path.startswith(('http://', 'https://')):
                full_image_path = os.path.join(os.path.dirname(md_file_path), image_path)
                if os.path.exists(full_image_path):
                    new_url = await upload_file(session, full_image_path, api_url)
                    if new_url:
                        new_url_match = re.search(r'"data":\["(.*?)"\]', new_url)
                        if new_url_match:
                            new_url = new_url_match.group(1)
                        else:
                            new_url = new_url.replace('"', '').replace('[', '').replace(']', '').replace('\n', '')
                        content = content.replace(f']({image_path})', f']({new_url})')
                        content = content.replace(f'src="{image_path}"', f'src="{new_url}"')
                        content = content.replace(f"src='{image_path}'", f"src='{new_url}'")
        
        # Process other file links
        for link in all_links:
            print(link)
            print(os.path.join(os.path.dirname(md_file_path), link))
            print(os.path.exists(os.path.join(os.path.dirname(md_file_path), link)))
            if not link.startswith(('http://', 'https://')) and os.path.exists(os.path.join(os.path.dirname(md_file_path), link)):
                full_file_path = os.path.join(os.path.dirname(md_file_path), link)
                new_url = await upload_file(session, full_file_path, api_url)
                if new_url:
                    new_url_match = re.search(r'"data":\["(.*?)"\]', new_url)
                    if new_url_match:
                        new_url = new_url_match.group(1)
                    else:
                        new_url = new_url.replace('"', '').replace('[', '').replace(']', '').replace('\n', '')
                    content = content.replace(f']({link})', f']({new_url})')
    
    elif mode == 'pull':
        img_dir = os.path.join(os.path.dirname(md_file_path), 'img')
        os.makedirs(img_dir, exist_ok=True)

        for image_url in all_images:
            if image_url.startswith(('http://', 'https://')):
                parsed_url = urlparse(image_url)
                image_filename = os.path.basename(parsed_url.path)
                
                base, ext = os.path.splitext(image_filename)
                counter = 1
                while os.path.exists(os.path.join(img_dir, image_filename)):
                    image_filename = f"{base}_{counter}{ext}"
                    counter += 1
                
                save_path = os.path.join(img_dir, image_filename)
                save_path = save_path + ".png"
                
                new_path = await download_image(session, image_url, save_path)
                print(f"{image_url} {save_path}")
                if new_path:
                    relative_path = os.path.relpath(new_path, os.path.dirname(md_file_path))
                    relative_path = relative_path.replace('\\', '/')
                    
                    content = content.replace(f']({image_url})', f']({relative_path})')
                    content = content.replace(f'src="{image_url}"', f'src="{relative_path}"')
                    content = content.replace(f"src='{image_url}'", f"src='{relative_path}'")

    with open(md_file_path, 'w', encoding='utf-8') as file:
        file.write(content)
    print(f"Processed file: {md_file_path}")

# Function to process all markdown files in a directory
async def process_directory(directory, mode, api_url):
    ssl._create_default_https_context = ssl._create_unverified_context
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith('.md'):
                    md_file_path = os.path.join(root, file)
                    try:
                        await process_markdown_file(session, root, md_file_path, mode, api_url)
                    except Exception as e:
                        print(f"Error processing file {md_file_path}: {e}")

# Function to process a single file
async def process_single_file(file_path, mode, api_url):
    if not file_path.endswith('.md'):
        print(f"Error: {file_path} is not a Markdown file")
        return

    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
        try:
            await process_markdown_file(session, os.path.dirname(file_path), file_path, mode, api_url)
        except Exception as e:
            print(f"Error processing file {file_path}: {e}")

# Main function that processes the command line arguments
def main():
    parser = argparse.ArgumentParser(description="Process Markdown files' images and links.")
    parser.add_argument('-f', '--file', help="Path to a single Markdown file")
    parser.add_argument('-d', '--directory', help="Directory containing Markdown files")
    parser.add_argument('-m', '--mode', choices=['post', 'pull'], required=True, help="Mode of operation: 'post' to upload local images and files, 'pull' to download remote images")
    parser.add_argument('-s', '--server', default='http://localhost:8089/upload', help="URL of the upload server")
    
    args = parser.parse_args()

    if not args.file and not args.directory:
        print("Error: Either a file (-f) or a directory (-d) must be specified")
        return

    if args.file and args.directory:
        print("Error: Only one of file (-f) or directory (-d) can be specified")
        return

    if args.file:
        if not os.path.isfile(args.file):
            print(f"Error: File {args.file} does not exist")
            return
        asyncio.run(process_single_file(args.file, args.mode, args.server))
    elif args.directory:
        if not os.path.isdir(args.directory):
            print(f"Error: Directory {args.directory} does not exist")
            return
        asyncio.run(process_directory(args.directory, args.mode, args.server))

if __name__ == "__main__":
    main()
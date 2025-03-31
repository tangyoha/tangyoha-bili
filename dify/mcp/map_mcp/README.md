------

## 1. 环境准备

在开始之前，请确保已安装以下工具和软件：

- **Docker**：用于构建和运行容器化应用。
- **Docker Compose**：便于管理多容器应用。
- **文本编辑器**：用于编辑 Dockerfile、.env 和 docker-compose.yaml 文件。
- **网络环境**：保证能访问外网资源（例如下载安装脚本）。

------

## 2. 构建 Docker 镜像

### 2.1 创建 Dockerfile

在项目根目录下创建一个名为 `Dockerfile` 的文件，内容如下：

```dockerfile
# 使用指定的基础镜像
FROM langgenius/dify-plugin-daemon:0.0.6-local

# 安装 Node.js 环境（这里选择 Node.js 22 版本）
RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash -
RUN apt-get install nodejs -y

# 安装 npm 包管理器
RUN curl -qL https://www.npmjs.com/install.sh | sh
```

> **说明**：
>
> - 此 Dockerfile 基于 Dify 官方提供的插件守护进程镜像。
> - 使用 `curl` 命令安装 Node.js 与 npm，确保插件运行时有稳定的 Node 环境。

### 2.2 构建镜像

在终端中执行以下命令进行构建：

```bash
docker build -t dify-plugin:latest .
```

构建成功后，即可获得自定义的插件镜像 `dify-plugin:latest`。

### 2.3 或者直接使用我构建好的镜像

```
docker pull tangyoha/dify-plugin:latest
```



------

## 3. 安装 MCP Client 插件

为了让 Dify 应用支持 MCP 客户端功能，需要修改 Dify 的环境配置和服务配置文件。

### 3.1 修改环境变量文件 (.env)

在 Dify 项目的根目录下找到 `.env` 文件，定位到 `FORCE_VERIFYING_SIGNATURE` 参数，并将其设置为 `false`：

```dotenv
FORCE_VERIFYING_SIGNATURE=false
```

> **提示**：关闭签名校验有助于开发调试阶段减少因校验问题导致的启动错误。正式环境部署时建议开启签名验证以提高安全性。

### 3.2 修改 Docker Compose 配置

打开项目中的 `docker-compose.yaml` 文件，找到 `plugin_daemon` 服务的配置部分，将原有镜像修改为我们刚构建的 `dify-plugin:latest` 镜像：

```yaml
plugin_daemon:
  image: dify-plugin:latest # 如果你是拉的我的要改成 tangyoha/dify-plugin:latest
```

完成修改后，保存文件并重启 Dify 服务：

```bash
docker-compose down
docker-compose up -d
```

> **注意**：重启服务后，Dify 会加载最新的插件镜像，并根据环境变量配置启动 MCP 客户端插件。

### 3.3 安装dify mcp client

下载打开插件安装[dify-mcp-client.difypkg](./dify-mcp-client.difypkg)



------

## 4. 申请高德 API

为了让应用支持高德地图的功能，需要获取高德地图 MCP 服务的 API Key。步骤如下：

1. **访问高德开放平台**
    打开浏览器，进入高德开放平台 MCP 服务的入门页面：[高德地图 MCP 服务入门](https://lbs.amap.com/api/mcp-server/gettingstarted)。
2. **注册/登录账号**
    若还未注册，请先完成账号注册，然后登录高德开放平台。
3. **创建应用**
    在控制台中选择“创建新应用”，填写应用名称、描述及相关信息。创建完成后，会生成一个 API Key。
4. **配置权限和服务**
    根据项目需要，申请对应的地图数据服务权限，如地图展示、路径规划、地点检索等。

```json
{
    "mcpServers": {
        "amap-maps": {
            "command": "npx",
            "args": [
                "-y",
                "@amap/amap-maps-mcp-server"
            ],
            "env": {
                "AMAP_MAPS_API_KEY": "您在高德官网上申请的key"
            }
        }
    }
}
```



> **提示**：请认真阅读高德官方文档，确保 API Key 的申请和使用符合高德的使用规范和流量限制要求。

------

## 4. 大模型配置 【如果已经配置过了，请跳过】

------

### 4.1 注册siliconflow

使用这个 https://cloud.siliconflow.cn/i/bnRVlBpN 注册

注册好了后创建API key

在dify上安装 siliconflow 模型 输入API key

### 4.1  注册openroute

自行搜索

## 5. 在 Dify 上创建工作流

工作流是 Dify 应用中的核心业务逻辑单元，通过图形化界面配置不同的功能节点实现数据处理和业务逻辑的联动。

### 5.1 登录 Dify 平台

使用管理员账号登录 Dify 后台管理界面，进入“工作流管理”模块。

### 5.2 创建新工作流

1. 点击“新建工作流”，输入工作流名称和描述（例如“高德地图 MCP 集成工作流”）。
2. 在工作流设计器中，拖拽所需的节点到编辑区域：
   - **数据输入节点**：用于接收用户请求或外部数据。
   - **MCP 调用节点**：配置调用高德地图 API 的参数，包括在前面申请到的 API Key。
   - **数据处理节点**：对返回的地图数据进行格式化、过滤或进一步处理。
   - **输出节点**：展示或传递处理后的数据至前端应用或其他系统。

### 5.3 配置 MCP 调用节点

在 MCP 调用节点中：

- 输入高德 API Key。
- 设置请求参数（如位置查询、路径规划所需参数）。
- 测试节点调用，确保与高德地图服务的联通性正常。

### 5.4 保存与发布工作流

确认所有节点配置无误后，保存工作流并点击“发布”。此时，Dify 应用将根据新创建的工作流实现地图数据的实时交互。

------

## 6. 流程总结与后续调试

- **镜像构建**：利用 Dockerfile 构建自定义插件镜像，确保 Node.js 环境与依赖安装无误。
- **插件安装**：修改 .env 与 docker-compose.yaml 文件，确保 Dify 加载最新构建的 MCP client 插件。
- **高德 API 申请**：访问高德开放平台申请 API Key，并确保正确配置服务权限。
- **工作流创建**：在 Dify 平台上构建包含高德地图调用的工作流，实现地图数据的交互与展示。

> **后续工作建议**：
>
> - 对各步骤进行逐项测试，确保每个环节运行正常。
> - 根据实际需求调整工作流中的节点逻辑，优化数据处理流程。
> - 密切关注高德 API 的使用情况，及时调整流量控制和异常处理策略。

------

通过以上详细流程，您可以一步步完成 MCP 构建 Dify 应用并集成高德地图 MCP 服务的全过程。如果在操作过程中遇到问题，建议先逐步排查各环节配置是否正确，再参考高德和 Dify 的官方文档以获得更多帮助。
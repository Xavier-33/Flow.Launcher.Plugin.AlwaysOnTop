# 如何发布到 GitHub 并进入 Flow Launcher 插件商店

按顺序做即可。所有链接与作者信息已按 GitHub 用户名 **Xavier-33** 填好。

本插件固定 ID：

```
ee4eb44b-2b92-4ab0-beea-98b8bef27423
```

---

## 第一步：创建 GitHub 仓库

1. 打开 https://github.com/new  
2. Repository name：`Flow.Launcher.Plugin.AlwaysOnTop`  
3. Public  
4. **不要**勾选 “Add a README”（本地已有文件）  
5. Create repository  

本地上传：

```bash
cd Flow.Launcher.Plugin.AlwaysOnTop
# 先改 plugin.json 里的 Website 为自己的仓库地址
git init
git add .
git commit -m "Initial release: Always On Top v1.1.2"
git branch -M main
git remote add origin https://github.com/Xavier-33/Flow.Launcher.Plugin.AlwaysOnTop.git
git push -u origin main
```

---

## 第二步：改 plugin.json 里的 Website

把：

```json
"Website": "https://github.com/Xavier-33/Flow.Launcher.Plugin.AlwaysOnTop"
```

改成真实地址，再 commit / push。

---

## 第三步：打 Release（带 zip）

仓库已包含 `.github/workflows/PublishRelease.yml`。

### 方式 A：打 tag（推荐）

```bash
# 确认 plugin.json 的 Version 是 1.1.2
git tag v1.1.2
git push origin v1.1.2
```

### 方式 B：手动跑 Actions

GitHub → **Actions** → **Publish Release** → **Run workflow**

成功后在 **Releases** 里应有：

`Flow.Launcher.Plugin.AlwaysOnTop.zip`

下载链接形如：

```
https://github.com/Xavier-33/Flow.Launcher.Plugin.AlwaysOnTop/releases/download/v1.1.2/Flow.Launcher.Plugin.AlwaysOnTop.zip
```

---

## 第四步：提交到 Flow 插件清单

1. Fork：https://github.com/Flow-Launcher/Flow.Launcher.PluginsManifest  
2. 在 fork 的 `plugins/` 目录新建文件：

```
AlwaysOnTop-ee4eb44b-2b92-4ab0-beea-98b8bef27423.json
```

3. 内容（已填好）：

```json
{
  "ID": "ee4eb44b-2b92-4ab0-beea-98b8bef27423",
  "Name": "Always On Top",
  "Description": "Pin or unpin taskbar windows to stay always on top (like PowerToys Always On Top)",
  "Author": "Xavier-33",
  "Version": "1.1.2",
  "Language": "python",
  "Website": "https://github.com/Xavier-33/Flow.Launcher.Plugin.AlwaysOnTop",
  "UrlDownload": "https://github.com/Xavier-33/Flow.Launcher.Plugin.AlwaysOnTop/releases/download/v1.1.2/Flow.Launcher.Plugin.AlwaysOnTop.zip",
  "UrlSourceCode": "https://github.com/Xavier-33/Flow.Launcher.Plugin.AlwaysOnTop",
  "IcoPath": "https://cdn.jsdelivr.net/gh/Xavier-33/Flow.Launcher.Plugin.AlwaysOnTop@main/Images/app.png"
}
```

4. 向 **Flow-Launcher/Flow.Launcher.PluginsManifest** 的默认分支提 Pull Request  
5. 等待维护者审核合并  

官方说明：  
https://github.com/Flow-Launcher/Flow.Launcher.PluginsManifest  

---

## 第五步：等待上线

- 合并后，清单大约每 3 小时刷新一次  
- CDN 同步可能要 **几小时到几天**  
- 在此期间用户仍可手动安装：

```
pm install https://github.com/Xavier-33/Flow.Launcher.Plugin.AlwaysOnTop/releases/download/v1.1.2/Flow.Launcher.Plugin.AlwaysOnTop.zip
```

上线后：

```
pm install Always On Top
```

---

## 之后如何更新版本

1. 改代码 + 提高 `plugin.json` 的 `Version`（例如 `1.2.0`）  
2. `git tag v1.2.0 && git push origin v1.2.0`  
3. Actions 自动发新 Release  
4. **不用再提 Manifest PR** —— 官方 CI 会定时检测新版本并自动更新商店里的版本号  

---

## 商店政策（简要）

不允许：恶意代码、盗版、欺诈、不当内容、冒充等。  
详见 Manifest 仓库的 Plugin Store policy。

本插件仅使用公开 Win32 API 切换窗口 TOPMOST，符合政策。

---

## 常见问题

**Q: PR 很久没人审？**  
可到 [Flow Discord](https://discord.gg/flow-launcher) 友好提醒。

**Q: 图标 IcoPath 必须用 CDN？**  
是的，推荐 jsDelivr：  
`https://cdn.jsdelivr.net/gh/用户名/仓库@main/Images/app.png`

**Q: 必须用 GitHub Actions？**  
是官方要求，用于自动构建带依赖的 release zip。

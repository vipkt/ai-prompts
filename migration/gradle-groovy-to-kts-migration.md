# Gradle Groovy 转 KTS + Version Catalog

将整个项目的构建文件从 Groovy DSL 迁移到 Kotlin DSL，并统一使用 libs.versions.toml 管理所有依赖版本。

## 要求

- 读取 settings.gradle，通过 include() 自动识别所有模块
- 创建 gradle/libs.versions.toml，按以下格式定义：
  - [versions]：驼峰命名，compileSdk、minSdk、targetSdk 固定放在顶部，顺序为 compileSdk、minSdk、targetSdk
  - [libraries] / [bundles] / [plugins]：短横线命名
  - 示例：
    ```toml
    [versions]
    compileSdk = "35"
    minSdk = "23"
    targetSdk = "35"
    
    kotlin = "1.9.25"
    
    [libraries]
    kotlin-stdlib = { group = "org.jetbrains.kotlin", name = "kotlin-stdlib", version.ref = "kotlin" }
    
    [plugins]
    kotlin-android = { id = "org.jetbrains.kotlin.android", version.ref = "kotlin" }
    ```

- 将 settings.gradle 和所有 build.gradle 转换为 .kts 格式
- 版本配置读取逻辑：
  - versionCode / versionName：优先从 gradle.properties 读取（properties["VERSION_CODE"].toString().toInt() / properties["VERSION_NAME"].toString()），不存在则从 libs.versions.toml 读取（libs.versions.versionCode.get().toInt() / libs.versions.versionName.get()）
  - compileSdk / minSdk / targetSdk：固定从 libs.versions.toml 读取（libs.versions.compileSdk.get().toInt() 等）
- 迁移后使用 version catalog 语法：依赖用 implementation(libs.xxx)，插件用 alias(libs.plugins.xxx)
- 保留原有自定义任务和构建逻辑，仅转换语法
- 迁移完成后运行 ./gradlew build 验证

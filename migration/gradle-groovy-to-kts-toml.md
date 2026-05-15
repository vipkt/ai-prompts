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
    
    agp = "8.13.0"
    kotlin = "1.9.25"
    
    [libraries]
    kotlin-stdlib = { group = "org.jetbrains.kotlin", name = "kotlin-stdlib", version.ref = "kotlin" }
    
    [plugins]
    kotlin-android = { id = "org.jetbrains.kotlin.android", version.ref = "kotlin" }
    ```

- 将 settings.gradle 和所有 build.gradle 转换为 .kts 格式
- 版本配置读取逻辑：
  - versionCode / versionName 优先从 gradle.properties 中读取，如果存在则直接使用：
    ```kotlin
    // 从 gradle.properties 读取
    versionCode = properties["VERSION_CODE"].toString().toInt()
    versionName = properties["VERSION_NAME"].toString()
    ```
  - 如果 gradle.properties 中不存在版本定义，则在 libs.versions.toml 中进行定义，然后使用：
    ```kotlin
    // 从 libs.versions.toml 读取
    versionCode = libs.versions.versionCode.get().toInt()
    versionName = libs.versions.versionName.get()
    ```
- 迁移后使用 version catalog 语法：依赖用 implementation(libs.xxx)，插件用 alias(libs.plugins.xxx)
- 保留原有自定义任务和构建逻辑，仅转换语法
- 迁移完成后运行 ./gradlew build 验证

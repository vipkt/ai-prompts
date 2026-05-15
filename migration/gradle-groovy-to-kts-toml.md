# Gradle Groovy 转 KTS + Version Catalog

将整个项目的构建文件从 Groovy DSL 迁移到 Kotlin DSL，并统一使用 libs.versions.toml 管理所有依赖版本、插件、依赖声明。

## 要求

- 读取 settings.gradle，通过 include() 自动识别所有模块
- 创建 gradle/libs.versions.toml，目录结构建议如下：

  ```
  gradle/
    └── libs.versions.toml   // 统一管理所有版本号、依赖和插件
  ```

- 依赖、插件、版本定义规范：

  - [versions]：统一写在顶部，采用驼峰命名，compileSdk、minSdk、targetSdk 固定顺序（compileSdk、minSdk、targetSdk），其余依赖版本按需追加
  - [libraries] / [plugins]：统一声明所有依赖和插件，命名风格建议短横线命名
  - [bundles]：如需依赖组合，可统一归档

  **示例代码：**

  ```toml
  [versions]
  compileSdk = "35"
  minSdk = "23"
  targetSdk = "35"

  agp = "8.13.0"
  kotlin = "1.9.25"
  # 其他依赖版本...
  
  [libraries]
  kotlin-stdlib = { group = "org.jetbrains.kotlin", name = "kotlin-stdlib", version.ref = "kotlin" }
  # 其他依赖...
  
  [plugins]
  kotlin-android = { id = "org.jetbrains.kotlin.android", version.ref = "kotlin" }
  android-application = { id = "com.android.application", version.ref = "agp" }
  # 其他插件...
  ```

- 将 settings.gradle 和所有 build.gradle 转换为 .kts 格式，并通过 version catalog 统一引用依赖、插件，如：

  ```kotlin
  // build.gradle.kts
  plugins {
      alias(libs.plugins.kotlin.android)
      // alias(libs.plugins.android.application) // 如需用 AGP 插件
      // 其他插件...
  }

  android {
      compileSdk = libs.versions.compileSdk.get().toInt()
      defaultConfig {
          minSdk = libs.versions.minSdk.get().toInt()
          targetSdk = libs.versions.targetSdk.get().toInt()
          // ...
      }
      // ...
  }

  dependencies {
      implementation(libs.kotlin.stdlib)
      // 其他依赖...
  }
  ```

- 版本配置读取逻辑：
  - versionCode / versionName 优先从 gradle.properties 中读取，如果存在则直接使用：
    ```kotlin
    // 从 gradle.properties 读取
    versionCode = properties["VERSION_CODE"].toString().toInt()
    versionName = properties["VERSION_NAME"].toString()
    ```
  - 如果 gradle.properties 中不存在版本定义，则在 libs.versions.toml 中定义，然后引用：
    ```kotlin
    // 从 libs.versions.toml 读取（假设有 versionCode/versionName 字段）
    versionCode = libs.versions.versionCode.get().toInt()
    versionName = libs.versions.versionName.get()
    ```

- 迁移后依赖和插件全部通过 version catalog（libs.versions、libs、libs.plugins）统一方式引用，版本号通过 [versions] 管理
- 保留原有自定义任务和构建逻辑，仅转换语法
- 迁移完成后运行 ./gradlew build 验证

## libs.versions.toml 结构完整示例

```toml
# gradle/libs.versions.toml
[versions]
compileSdk = "35"
minSdk = "23"
targetSdk = "35"

agp = "8.13.0"
kotlin = "1.9.25"
# 可增加更多依赖版本...

[libraries]
kotlin-stdlib = { group = "org.jetbrains.kotlin", name = "kotlin-stdlib", version.ref = "kotlin" }
# 可增加更多依赖声明...

[plugins]
kotlin-android = { id = "org.jetbrains.kotlin.android", version.ref = "kotlin" }
android-application = { id = "com.android.application", version.ref = "agp" }
# 可增加更多插件声明...
```

## 统一用法

**build.gradle.kts 内调用示例：**

```kotlin
plugins {
    alias(libs.plugins.kotlin.android)
    // alias(libs.plugins.android.application)
    // 其他插件
}

android {
    compileSdk = libs.versions.compileSdk.get().toInt()
    defaultConfig {
        minSdk = libs.versions.minSdk.get().toInt()
        targetSdk = libs.versions.targetSdk.get().toInt()
        // 其他配置...
    }
    // ...
}

dependencies {
    implementation(libs.kotlin.stdlib)
    // 其他依赖...
}
```

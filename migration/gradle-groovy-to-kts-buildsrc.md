# Gradle Groovy 转 KTS + buildSrc 版本管理

将整个项目的构建文件从 Groovy DSL 迁移到 Kotlin DSL，并通过 buildSrc 统一管理所有依赖版本、插件、依赖声明。

## 要求

- 读取 settings.gradle，通过 include() 自动识别所有模块
- 创建 buildSrc 管理依赖和版本，目录结构建议如下：

  ```
  buildSrc/
    └── src/main/kotlin/
        ├── Versions.kt         // 统一管理所有版本号
        ├── Dependencies.kt     // 统一声明所有依赖
        └── Plugins.kt          // 统一声明所有插件
  ```

- 依赖、插件、版本定义规范：

  - 版本号统一写在 Versions.kt 中，采用驼峰命名，compileSdk、minSdk、targetSdk 固定放在顶部（顺序为 compileSdk、minSdk、targetSdk），其余依赖版本按需追加
  - Dependencies.kt 用于统一声明依赖，命名规则建议驼峰式或下划线，建议始终保持风格一致，通过字符串模板引用 Versions.kt 中的版本常量
  - Plugins.kt 用于统一声明插件 id 及版本号字符串

  **示例代码：**

  ```kotlin
  // Versions.kt
  object Versions {
      const val compileSdk = 35
      const val minSdk = 23
      const val targetSdk = 35

      const val agp = "8.13.0"
      const val kotlin = "1.9.25"
      // 其他依赖版本...
  }
  ```

  ```kotlin
  // Dependencies.kt
  object Dependencies {
      const val kotlinStdlib = "org.jetbrains.kotlin:kotlin-stdlib:${Versions.kotlin}"
      // 其他依赖...
  }
  ```

  ```kotlin
  // Plugins.kt
  object Plugins {
      const val kotlinAndroid = "org.jetbrains.kotlin.android"
      const val android = "com.android.application"
      // 其他插件...
  }
  ```

- 将 settings.gradle 和所有 build.gradle 转换为 .kts 格式，并通过 buildSrc 统一引用依赖、插件，如：

  ```kotlin
  // build.gradle.kts
  plugins {
      id(Plugins.kotlinAndroid) version Versions.kotlin
      // 其他插件声明...
  }

  android {
      compileSdk = Versions.compileSdk
      defaultConfig {
          minSdk = Versions.minSdk
          targetSdk = Versions.targetSdk
          // ...
      }
  }

  dependencies {
      implementation(Dependencies.kotlinStdlib)
      // 其他依赖声明...
  }
  ```

- 版本配置读取逻辑：
  - 先读取 gradle.properties 文件，看是否存在版本定义（VERSION_CODE / VERSION_NAME），如果存在（此时 libs.versions.toml 中无需再定义 versionCode / versionName），直接使用：
    ```kotlin
     defaultConfig {
        // 从 gradle.properties 读取
        versionCode = properties["VERSION_CODE"].toString().toInt()
        versionName = properties["VERSION_NAME"].toString()
    }
    ```
  - 如果 gradle.properties 中不存在版本定义，则在 buildSrc 的 Versions.kt 里进行定义然后直接引用：
    ```kotlin
    defaultConfig {
      // 从 Versions.kt 读取（假设 Versions.kt 里有 versionCode/versionName 字段）
      versionCode = Versions.versionCode
      versionName = Versions.versionName
    }
    ```

- 迁移后依赖和插件全部通过 Dependencies 和 Plugins 统一方式引用，版本号通过 Versions 管理
- 保留原有自定义任务和构建逻辑，仅转换语法
- 迁移完成后运行 ./gradlew build 验证

## buildSrc 结构完整示例

```kotlin
// buildSrc/src/main/kotlin/Versions.kt
object Versions {
    const val compileSdk = 35
    const val minSdk = 23
    const val targetSdk = 35

    const val agp = "8.13.0"
    const val kotlin = "1.9.25"
    // 可增加更多依赖版本...
}
```

```kotlin
// buildSrc/src/main/kotlin/Dependencies.kt
object Dependencies {
    const val kotlinStdlib = "org.jetbrains.kotlin:kotlin-stdlib:${Versions.kotlin}"
    // 可增加更多依赖...
}
```

```kotlin
// buildSrc/src/main/kotlin/Plugins.kt
object Plugins {
    const val kotlinAndroid = "org.jetbrains.kotlin.android"
    const val androidApplication = "com.android.application"
    // 可增加更多插件声明...
}
```

## 统一用法

**build.gradle.kts 内调用示例：**

```kotlin
plugins {
    id(Plugins.kotlinAndroid) version Versions.kotlin
    // id(Plugins.androidApplication) version Versions.agp // 如需用 AGP 插件
    // 其他插件...
}

android {
    compileSdk = Versions.compileSdk
    defaultConfig {
        minSdk = Versions.minSdk
        targetSdk = Versions.targetSdk
        // 其他配置...
    }
    // ...
}

dependencies {
    implementation(Dependencies.kotlinStdlib)
    // 其他依赖...
}
```

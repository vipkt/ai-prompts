# ai-prompts
精心整理的 AI 提示词集合

### Prompts / 提示

<!-- prompts start -->
## [Migration / 迁移](migration)
[Gradle Groovy 转 KTS + buildSrc 版本管理](migration/gradle-groovy-to-kts-buildsrc.md)
[Gradle Groovy 转 KTS + Version Catalog](migration/gradle-groovy-to-kts-toml.md)
<!-- prompts end -->

### 自动更新 / Automation

- 本地执行：`python scripts/update_readme_prompts.py`
- GitHub Actions：`.github/workflows/update-readme-prompts.yml`
  - 支持手动触发（`workflow_dispatch`）
  - 支持定时触发（每周一 03:17 UTC）自动刷新 README 中 prompts 区域

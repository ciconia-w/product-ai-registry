# deepin v20 vs v25 兼容性差异与 AI 开发约束

> 本文件为 AI 可读规则集。开发 deepin 应用时严格执行以下约束，避免兼容性返工。

---

## 快速判断：当前目标平台

| 目标 | 特征 |
|------|------|
| 仅 v20 | control 文件中依赖 libqt5 / libdtk5 |
| 仅 v25 | linglong.yaml 或依赖 libqt6 / libdtk6 |
| 双版本 | CMakeLists.txt 含 QT_VERSION_MAJOR 变量 |

---

## Python 约束

### 仅限 v20 目标（Python 3.7.3）

**禁止使用：**
- 海象运算符 `:=`（3.8+）
- 函数定义中的 `/` 位置参数（3.8+）
- f-string 调试语法 `f"{x=}"`（3.8+）
- `dict | dict` 合并运算符（3.9+），改用 `{**a, **b}`
- `list[str]` / `dict[str, int]` 直接作为类型注解（3.9+），改用 `typing.List[str]`
- `str | None` 联合类型注解（3.10+），改用 `Optional[str]`
- `match / case`（3.10+）
- `asyncio.TaskGroup`（3.11+）
- `tomllib`（3.11+）
- `ExceptionGroup`（3.11+）
- `typing.Self`（3.11+）

**必须使用：**
```python
from typing import Optional, List, Dict, Tuple, Union
from __future__ import annotations  # 若需要 PEP 563 延迟注解
```

### 双版本（以 v20 为基准）

Python 语法严格限制在 3.7 范围内。

---

## Qt/DTK 约束

### 双版本 CMakeLists.txt 必须写法

```cmake
# 自动检测 Qt 版本，切勿硬编码 Qt5 或 Qt6
find_package(QT NAMES Qt6 Qt5 REQUIRED COMPONENTS Core)
find_package(Qt${QT_VERSION_MAJOR} REQUIRED COMPONENTS Core Widgets DBus)
find_package(Dtk${QT_VERSION_MAJOR}Widget REQUIRED)
find_package(Dtk${QT_VERSION_MAJOR}Core REQUIRED)
find_package(Dtk${QT_VERSION_MAJOR}Gui REQUIRED)
```

### Qt5（v20）vs Qt6（v25）API 差异

| 功能 | v20 (Qt5) | v25 (Qt6) |
|------|-----------|-----------|
| 事件循环 | `app.exec_()` | `app.exec()` |
| 对齐枚举 | `Qt.AlignLeft` | `Qt.AlignmentFlag.AlignLeft` |
| SizePolicy | `QSizePolicy.Expanding` | `QSizePolicy.Policy.Expanding` |
| 字体粗细 | `QFont.Bold` | `QFont.Weight.Bold` |
| 窗口类型 | `Qt.Window` | `Qt.WindowType.Window` |
| X11 额外信息 | `Qt5X11Extras` | `QGuiApplication::nativeInterface()` |
| WebKit | `QWebKitWidgets` | 已移除，改用 `QWebEngineWidgets` |
| PyQt import | `from PyQt5.QtWidgets import` | `from PyQt6.QtWidgets import` |

### Python 中动态适配 Qt 版本

```python
try:
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import Qt
    PYQT_VERSION = 6
except ImportError:
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtCore import Qt
    PYQT_VERSION = 5
```

---

## D-Bus 服务名约束（关键！）

命名空间在 v20 和 v25 之间**完全不同**，硬编码服务名会导致一个版本上调用失败。

**必须使用版本条件判断：**

```python
import subprocess

def get_deepin_version():
    try:
        result = subprocess.run(
            ['cat', '/etc/os-release'],
            capture_output=True, text=True
        )
        for line in result.stdout.splitlines():
            if line.startswith('VERSION_ID='):
                return int(line.split('=')[1].strip('"'))
    except Exception:
        pass
    return 20  # 默认回退到 v20

DEEPIN_VERSION = get_deepin_version()

# D-Bus 服务名映射
if DEEPIN_VERSION >= 25:
    DBUS_APPEARANCE   = "org.deepin.dde.Appearance1"
    DBUS_DISPLAY      = "org.deepin.dde.Display1"   # 若存在
    DBUS_SESSION      = "org.deepin.dde.Session1"
    DBUS_DOCK         = "org.deepin.dde.Dock1"
    DBUS_WMSWITCHER   = "org.deepin.dde.WMSwitcher1"
    DBUS_SYSINFO      = "org.deepin.dde.SystemInfo1"
    DBUS_CLIPBOARD    = "org.deepin.dde.Clipboard1"
    DBUS_TRAY         = "org.deepin.dde.TrayManager1"
    DBUS_NETWORK      = "org.deepin.dde.Network1"    # 若存在
else:
    DBUS_APPEARANCE   = "com.deepin.daemon.Appearance"
    DBUS_DISPLAY      = "com.deepin.daemon.Display"
    DBUS_SESSION      = "com.deepin.SessionManager"
    DBUS_DOCK         = "com.deepin.dde.Dock"
    DBUS_WMSWITCHER   = "com.deepin.WMSwitcher"
    DBUS_SYSINFO      = "com.deepin.daemon.SystemInfo"
    DBUS_CLIPBOARD    = "com.deepin.dde.Clipboard"
    DBUS_TRAY         = "com.deepin.dde.TrayManager"
    DBUS_NETWORK      = "com.deepin.daemon.Network"
```

---

## OpenSSL / TLS 约束

| | v20 | v25 |
|-|-----|-----|
| 版本 | 1.1.1d | 3.2.4 |
| Python ssl | TLS 1.2 默认 | TLS 1.3 支持 |

**双版本安全写法（Python）：**
- 优先使用 `ssl` / `hashlib` 标准库，避免直接调用 `cryptography` 包的低级 API
- 不使用 `ssl.OP_NO_SSLv2/v3`（v20 可能无此常量）
- 若必须用 `cryptography`，限定版本 `>=3.0,<42`

---

## 打包约束

### 双版本 debian 控制文件

```
debian/
  control        ← v25 (Qt6 依赖)
  control.1      ← v20 (Qt5 依赖)
```

`control` 示例依赖片段：
```
Depends: libdtk6widget (>= 6.0), libqt6widgets6 (>= 6.4)
```

`control.1` 示例依赖片段：
```
Depends: libdtkwidget5 (>= 5.6), libqt5widgets5 (>= 5.11)
```

### Linyaps (v25 专属)

- App ID 格式：`org.deepin.<appname>`（全小写，反向域名）
- 沙箱内无法访问 `/etc`、`/usr`，所有额外依赖须打进包内
- 配置文件写入 `$XDG_CONFIG_HOME`，数据写入 `$XDG_DATA_HOME`
- D-Bus 通过 `ll-dbus-proxy` 代理，需在 `linglong.yaml` 中声明权限
- 不能直接读取宿主机 `/proc` 下的特权信息

---

## 兼容性速查

| 场景 | v20 | v25 | 双版本写法 |
|------|-----|-----|-----------|
| 读系统主题色 | `com.deepin.daemon.Appearance` | `org.deepin.dde.Appearance1` | 版本条件分支 |
| PyQt | PyQt5 | PyQt6 | try/except import |
| 类型注解 | `Optional[str]` | `str \| None` | 用 Optional |
| CMake Qt 依赖 | `Qt5Widgets` | `Qt6Widgets` | `Qt${QT_VERSION_MAJOR}Widgets` |
| 事件循环 | `.exec_()` | `.exec()` | 版本条件或 `getattr` |
| 颜色设置读取 | libqt5xdg3 | libgsettings-qt6 | 版本条件 |
| 打包 | deb only | linyaps 优先 | 双 control 文件 |

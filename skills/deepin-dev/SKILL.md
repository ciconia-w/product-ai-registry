---
name: deepin-dev
version: 0.1.0
description: deepin v20/v25 双版本应用开发约束 - 自动防止 Qt/DTK/Python/D-Bus 兼容性返工
---

# deepin-dev

## Purpose

为 deepin v20（Qt5/Python3.7）和/或 v25（Qt6/Python3.12）应用开发提供强制兼容约束，防止 vibecoding 产出的代码在目标平台上运行失败或需要大量返工。

## When to activate

在以下情况自动应用本 skill 的全部约束：

- 文件中出现 `DtkWidget`、`DtkCore`、`DtkGui`、`DTK`、`dtk`
- 文件中出现 `from PyQt5` 或 `from PyQt6`
- 目录中存在 `debian/control`、`linglong.yaml`、`linyaps.yaml`
- 文件中出现 `com.deepin` 或 `org.deepin` D-Bus 服务名
- 用户提到 deepin、UOS、统信、v20、v25

## Platform detection

执行任何代码生成前，先确定目标平台：

1. 检查 `debian/control` 依赖：含 `libqt5` → v20，含 `libqt6` 或 `libdtk6` → v25
2. 检查 `CMakeLists.txt`：含 `Qt5` 硬编码 → v20，`Qt6` → v25，`QT_VERSION_MAJOR` → 双版本
3. 检查 `linglong.yaml` 存在 → v25
4. 无法判断时，**默认按双版本约束处理**（取最严格标准）

---

## RULE SET

### [PYTHON] 版本约束

**当目标包含 v20 时（Python 3.7.3），以下语法禁止使用：**

```
❌ x := expr                    # 海象运算符，3.8+
❌ def f(a, /, b)               # 位置参数 /，3.8+
❌ f"{value=}"                  # f-string 调试，3.8+
❌ {**a} | {**b}  →  用 {**a, **b}  # dict 合并，3.9+
❌ list[str]  →  用 List[str]   # 内置泛型，3.9+
❌ str | None  →  用 Optional[str]  # 联合类型，3.10+
❌ match x: case ...:           # match/case，3.10+
❌ asyncio.TaskGroup            # 3.11+
❌ tomllib                      # 3.11+
❌ ExceptionGroup               # 3.11+
❌ typing.Self                  # 3.11+
```

**v20 必须在文件顶部添加：**
```python
from typing import Optional, List, Dict, Tuple, Union, Any
```

### [QT] 双版本 CMake 必须写法

```cmake
# ✅ 正确：自动适配 Qt 版本
find_package(QT NAMES Qt6 Qt5 REQUIRED COMPONENTS Core)
find_package(Qt${QT_VERSION_MAJOR} REQUIRED COMPONENTS Core Widgets DBus)
find_package(Dtk${QT_VERSION_MAJOR}Widget REQUIRED)
find_package(Dtk${QT_VERSION_MAJOR}Core REQUIRED)
find_package(Dtk${QT_VERSION_MAJOR}Gui REQUIRED)

# ❌ 错误：不能硬编码版本号
find_package(Qt5 REQUIRED COMPONENTS Widgets)
find_package(Dtk6Widget REQUIRED)
```

### [QT] Python 中的 Qt 版本兼容写法

```python
# ✅ 双版本自动适配
try:
    from PyQt6.QtWidgets import QApplication, QWidget, QMainWindow
    from PyQt6.QtCore import Qt, QTimer
    from PyQt6.QtGui import QFont, QIcon
    PYQT_VERSION = 6
except ImportError:
    from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow
    from PyQt5.QtCore import Qt, QTimer
    from PyQt5.QtGui import QFont, QIcon
    PYQT_VERSION = 5

# ✅ 枚举兼容写法
if PYQT_VERSION >= 6:
    ALIGN_LEFT = Qt.AlignmentFlag.AlignLeft
    SIZE_EXPANDING = QSizePolicy.Policy.Expanding
else:
    ALIGN_LEFT = Qt.AlignLeft
    SIZE_EXPANDING = QSizePolicy.Expanding

# ✅ exec() 兼容写法
sys.exit(app.exec() if PYQT_VERSION >= 6 else app.exec_())
```

### [DBUS] 服务名必须版本条件化

D-Bus 命名空间在 v20/v25 之间完全不同，**禁止硬编码任一版本的服务名**。

```python
# ✅ 正确：运行时判断版本
import os

def _deepin_version() -> int:
    try:
        with open('/etc/os-release') as f:
            for line in f:
                if line.startswith('VERSION_ID='):
                    return int(line.split('=')[1].strip().strip('"'))
    except Exception:
        pass
    return 20

_VER = _deepin_version()

DBUS_APPEARANCE  = "org.deepin.dde.Appearance1"  if _VER >= 25 else "com.deepin.daemon.Appearance"
DBUS_SESSION     = "org.deepin.dde.Session1"      if _VER >= 25 else "com.deepin.SessionManager"
DBUS_DOCK        = "org.deepin.dde.Dock1"         if _VER >= 25 else "com.deepin.dde.Dock"
DBUS_WMSWITCHER  = "org.deepin.dde.WMSwitcher1"  if _VER >= 25 else "com.deepin.WMSwitcher"
DBUS_SYSINFO     = "org.deepin.dde.SystemInfo1"  if _VER >= 25 else "com.deepin.daemon.SystemInfo"
DBUS_CLIPBOARD   = "org.deepin.dde.Clipboard1"   if _VER >= 25 else "com.deepin.dde.Clipboard"
DBUS_TRAY        = "org.deepin.dde.TrayManager1" if _VER >= 25 else "com.deepin.dde.TrayManager"
DBUS_NETWORK     = "org.deepin.dde.Network1"     if _VER >= 25 else "com.deepin.daemon.Network"
DBUS_AUDIO       = "org.deepin.dde.Audio1"       if _VER >= 25 else "com.deepin.daemon.Audio"
DBUS_DISPLAY     = "org.deepin.dde.Display1"     if _VER >= 25 else "com.deepin.daemon.Display"
DBUS_POWER       = "org.deepin.dde.Power1"       if _VER >= 25 else "com.deepin.daemon.Power"
DBUS_KEYBINDING  = "org.deepin.dde.Keybinding1"  if _VER >= 25 else "com.deepin.daemon.Keybinding"
```

### [PACKAGE] Debian 双控制文件

```
debian/control    → v25（Qt6/DTK6 依赖）
debian/control.1  → v20（Qt5/DTK5 依赖）
```

v25 control 依赖示例：
```
Build-Depends: libdtk6widget-dev, qt6-base-dev
Depends: libdtk6widget (>= 6.0), libqt6widgets6
```

v20 control.1 依赖示例：
```
Build-Depends: libdtkwidget-dev (>= 5.6), qtbase5-dev
Depends: libdtkwidget5 (>= 5.6), libqt5widgets5
```

### [PACKAGE] Linyaps（v25 打包）

```yaml
# linglong.yaml 权限声明示例
permissions:
  dbus:
    session:
      - org.deepin.dde.Appearance1
      - org.deepin.dde.Dock1
```

- 配置文件：写入 `os.environ.get('XDG_CONFIG_HOME', os.path.expanduser('~/.config'))`
- 数据文件：写入 `os.environ.get('XDG_DATA_HOME', os.path.expanduser('~/.local/share'))`
- **禁止**：硬编码 `/etc/`、`/usr/share/` 作为配置读取路径

### [OPENSSL] SSL/TLS 安全写法

```python
# ✅ 通用写法（v20 1.1.1 和 v25 3.x 均兼容）
import ssl, hashlib

ctx = ssl.create_default_context()
# 不设置 OP_NO_SSLv2/v3（v20 可能无此常量）

# ✅ 哈希：直接用标准库
digest = hashlib.sha256(data).hexdigest()

# ❌ 避免直接使用 cryptography 包的低级 API
# 若必须使用 cryptography，限定 >=3.0,<42
```

---

## Review checklist

生成代码后，执行以下检查：

- [ ] Python 语法未超出目标版本范围
- [ ] 无硬编码 Qt5/Qt6 的 CMake find_package
- [ ] D-Bus 服务名通过版本条件动态选择
- [ ] PyQt import 有 try/except 兼容双版本
- [ ] linglong 打包中配置路径使用 XDG 变量
- [ ] debian/control 和 debian/control.1 分别针对 v25/v20
- [ ] 无直接读取 /etc、/usr 的硬编码路径（linglong 沙箱内）

---

## References

- 完整环境数据：`references/deepin-compat/v20.md`（v20）、`references/deepin-compat/v25.md`（v25）
- 差异与规则来源：`references/deepin-compat/diff.md`

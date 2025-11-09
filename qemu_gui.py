import sys
import json
from PyQt6.QtWidgets import (
    QApplication, QWidget, QDialog, QLabel, QLineEdit, QPushButton,
    QFileDialog, QVBoxLayout, QGridLayout, QScrollArea, QHBoxLayout, QTextEdit, QComboBox,
    QCheckBox, QListWidget, QMessageBox, QFormLayout, QMenu, QWizard, QWizardPage,
    QMenuBar
)
from PyQt6.QtCore import QProcess, Qt
from PyQt6.QtGui import QAction, QPalette, QColor, QGuiApplication
import profile_manager  
import qemu_config
from qemu_config import load_paths
from qemu_config import save_paths
import importlib

def load_language(lang_code):
    module = importlib.import_module(f"lang_{lang_code}")
    return module.translations
    
is_dark = QGuiApplication.styleHints().colorScheme().name == "Dark"

def is_dark_mode():
    palette = QGuiApplication.palette()
    bg_color = palette.color(QPalette.ColorRole.Window)
    return bg_color.lightness() < 128


class VMWizard(QWizard):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("New VM Configuration")
        self.setWizardStyle(QWizard.WizardStyle.ModernStyle)

        self.addPage(self.architecture_page())
        self.addPage(self.resources_page())
        self.addPage(self.disk_page())
        self.addPage(self.iso_page())
        self.addPage(self.bios_page())
        self.addPage(self.network_page())
        self.addPage(self.summary_page())

    def architecture_page(self):
        page = QWizardPage()
        page.setTitle("Architecture")
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Select Architecture:"))
        self.arch_combo = QComboBox()
        self.arch_combo.addItems(["x86_64", "arm", "aarch64", "riscv64"])
        layout.addWidget(self.arch_combo)
        page.setLayout(layout)
        return page

    def resources_page(self):
        page = QWizardPage()
        page.setTitle("Resources")
        layout = QVBoxLayout()
        layout.addWidget(QLabel("RAM (MB):"))
        self.ram_input = QLineEdit()
        layout.addWidget(self.ram_input)
        layout.addWidget(QLabel("CPU cores:"))
        self.cpu_input = QLineEdit()
        layout.addWidget(self.cpu_input)
        page.setLayout(layout)
        return page

    def disk_page(self):
        page = QWizardPage()
        page.setTitle("Disk")
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Disk path:"))
        self.disk_input = QLineEdit()
        browse_btn = QPushButton("Sfoglia...")
        browse_btn.clicked.connect(self.browse_disk)
        layout.addWidget(self.disk_input)
        layout.addWidget(browse_btn)
        page.setLayout(layout)
        return page

    def iso_page(self):
        page = QWizardPage()
        page.setTitle("ISO")
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Iso path:"))
        self.iso_input = QLineEdit()
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_iso)
        layout.addWidget(self.iso_input)
        layout.addWidget(browse_btn)
        page.setLayout(layout)
        return page
        
    def bios_page(self):
        page = QWizardPage()
        page.setTitle("BIOS / Firmware")
        layout = QVBoxLayout()
        layout.addWidget(QLabel("BIOS/UEFI path (optional):"))
        self.bios_input = QLineEdit()
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_bios)
        layout.addWidget(self.bios_input)
        layout.addWidget(browse_btn)
        page.setLayout(layout)
        return page

    def network_page(self):
        page = QWizardPage()
        page.setTitle("Network")
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Network mode:"))
        self.net_combo = QComboBox()
        self.net_combo.addItems(["user", "tap", "bridge"])
        layout.addWidget(self.net_combo)
        
        page.setLayout(layout)
        return page

    def summary_page(self):
        page = QWizardPage()
        page.setTitle("Summary")
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Click End to load VM..."))
        page.setLayout(layout)
        return page

    def browse_disk(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select disk image")
        if file:
            self.disk_input.setText(file)
    def browse_iso(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select ISO Image")
        if file_path:
            self.iso_input.setText(file_path)
    def browse_bios(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select BIOS/UEFI")
        if file:
            self.bios_input.setText(file)

    def get_vm_config(self):
        return {
            "arch": self.arch_combo.currentText(),
            "ram": self.ram_input.text(),
            "cpu": self.cpu_input.text(),
            "disk": self.disk_input.text(),
            "iso": self.iso_input.text(),
            "bios": self.bios_input.text(),
            "net": self.net_combo.currentText(),
          
        }


        
   





class QemuConfigDialog(QDialog):
    def __init__(self, paths, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configure Qemu Binaries")
        self.paths = load_paths()
        self.inputs = {}
        self.resize(1024, 768)
        layout = QVBoxLayout(self)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        grid = QGridLayout(container)

        keys = sorted(self.paths.keys())
        half = (len(keys) + 1) // 2
       

        for i, arch in enumerate(keys):
            col = 0 if i < half else 2
            row = i if i < half else i - half

            label = QLabel(arch)
            input_field = QLineEdit(self.paths[arch])
            self.inputs[arch] = input_field

            grid.addWidget(label, row, col)
            grid.addWidget(input_field, row, col + 1)

        scroll.setWidget(container)
        layout.addWidget(scroll)

        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_and_close)
        layout.addWidget(save_button)

    def save_and_close(self):
        updated = {arch: field.text() for arch, field in self.inputs.items()}
        save_paths(updated)
        self.accept()


class QemuLauncher(QWidget):
    


    def change_language(self, lang_code):
        lang_module = importlib.import_module(f"lang_{lang_code}")
        self.translations = lang_module.translations
        self.update_ui_texts()


    def open_config_dialog(self):
        dialog = QemuConfigDialog(self)
        dialog.exec()
        self.qemu_paths = qemu_config.load_paths()
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QEMU Launcher")
        self.setGeometry(100, 100, 700, 500)
        self.init_ui()
        self.qemu_paths = qemu_config.load_paths()

    def show_about(self):
        QMessageBox.information(self, "About", "Created by Takeshi\nVersion: 0.99\nEmail: nathangray1981@msn.com")

    def init_ui(self):
        main_layout = QHBoxLayout()
        config_layout = QVBoxLayout()
        menu_bar = QMenuBar(self)

        # Menu "Info"
        self.info_menu = QMenu("Info", self)
        self.about_action = QAction("About", self)
        self.about_action.triggered.connect(self.show_about)
        self.info_menu.addAction(self.about_action)

        # Menu "Lingua"
        self.lang_menu = QMenu("Language", self)
        for lang_code in ["it", "en", "fr"]:
            lang_action = QAction(lang_code.upper(), self)
            lang_action.triggered.connect(lambda checked, code=lang_code: self.change_language(code))
            self.lang_menu.addAction(lang_action)

        menu_bar.addMenu(self.info_menu)
        menu_bar.addMenu(self.lang_menu)

        main_layout.setMenuBar(menu_bar)
        # Sezione profili
        self.profile_list = QListWidget()
        self.refresh_profiles()

        profile_buttons = QHBoxLayout()
        self.load_button = QPushButton("Load Profile")
        self.load_button.clicked.connect(self.load_selected_profile)
        self.delete_button = QPushButton("Delete Profile")
        self.delete_button.clicked.connect(self.delete_selected_profile)
        profile_buttons.addWidget(self.load_button)
        profile_buttons.addWidget(self.delete_button)

        profile_section = QVBoxLayout()
        self.profile_label = QLabel("Available Profiles:")
        profile_section.addWidget(self.profile_label)
        profile_section.addWidget(self.profile_list)
        profile_section.addLayout(profile_buttons)

        # Campi configurazione
        self.arch_combo = QComboBox()
        self.arch_combo.addItems([
           
           
            "x86_64",
            "x86_64w",
            "aarch64",
            "aarch64w",
            "alpha",
            "alphaw",
            "arm",
            "armw",
            "avr",
            "avrw",
            "hppa",
            "hppaw",
            "i386",
            "i386w",
            "loongarch64",
            "loongarch64w",
            "microblaze",
            "microblazeel",
            "microblazeelw",
            "mips",
            "mips64",
            "mips64el",
            "mips64elw",
            "mips64w",
            "mipsel",
            "mipselw",
            "mipsw",
            "or1k",
            "or1kw",
            "ppc",
            "ppc64",
            "ppc64w",
            "riscv32",
            "riscv32w",
            "riscv64",
            "riscv64w",
            "rx",
            "rxw",
            "s390x",
            "s390xw",
            "sh4",
            "sh4eb",
            "sh4ebw",
            "sparc",
            "sparc64",
            "sparc64w",
            "sparcw",
            "tricore",
            "tricorew",
            "xtensa",
            "xtensaeb",
            "ztensaebw",
            "xtensaw"
        ])
        self.disk_input = QLineEdit()
        self.disk_button = QPushButton("Browse")
        self.disk_button.clicked.connect(self.browse_disk)

        self.iso_input = QLineEdit()
        self.iso_button = QPushButton("Browse")
        self.iso_button.clicked.connect(self.browse_iso)

        self.ram_input = QLineEdit("1024")
        self.cpu_input = QLineEdit("2")
        self.machine_input = QLineEdit()
        self.cpu_model_input = QLineEdit()
        self.bios_input = QLineEdit()
        self.bios_button = QPushButton("Browse BIOS")
        self.bios_button.clicked.connect(self.browse_bios)
        self.net_combo = QComboBox()
        self.net_combo.addItems(["user (NAT)", "bridge"])

        self.snapshot_checkbox = QCheckBox("Launch as snapshot")

        # Log console
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)

        # Pulsanti
        button_layout = QHBoxLayout()
        self.launch_button = QPushButton("Launch VM")
        self.launch_button.clicked.connect(self.launch_vm)

        self.save_button = QPushButton("Save Profile")
        self.save_button.clicked.connect(self.save_as_profile)

        button_layout.addWidget(self.launch_button)
        button_layout.addWidget(self.save_button)

        # Layout configurazione
        self.disk_label = QLabel("Disk Image:")
        config_layout.addWidget(self.disk_label)
        config_layout.addWidget(self.disk_input)
        config_layout.addWidget(self.disk_button)

        config_layout.addWidget(QLabel("ISO Image:"))
        config_layout.addWidget(self.iso_input)
        config_layout.addWidget(self.iso_button)

        config_layout.addWidget(QLabel("RAM (MB):"))
        config_layout.addWidget(self.ram_input)

        config_layout.addWidget(QLabel("CPU:"))
        config_layout.addWidget(self.cpu_input)
        self.vga_combo = QComboBox()
        self.vga_combo.addItems([
            "none",
            "VGA",
            "cirrus-vga",
            "qxl",
            "virtio-gpu-pci",
            "vmware-svga",
            "bochs-display"
        ])
        self.usb_bus_combo = QComboBox()
        self.usb_bus_combo.addItems([
            "No USB",
            "usb-uhci (USB 1.1)",
            "usb-ehci (USB 2.0)",
            "qemu-xhci (USB 3.0)"
        ])
        self.usb_bus_label = QLabel("USB Controller:")
        config_layout.addWidget(self.usb_bus_label)
        config_layout.addWidget(self.usb_bus_combo)
        self.input_combo = QComboBox()
        self.input_combo.addItems([
            "No input",
            "usb-kbd + usb-mouse",
            "usb-kbd + usb-tablet",
            "usb-kbd + usb-mouse + usb-tablet"
        ])
        self.disk_type_combo = QComboBox()
        self.disk_type_combo.addItems([
            "ide",
            "scsi",
            "virtio-blk",
            "usb-storage"
        ])
        self.accel_combo = QComboBox()
        self.accel_combo.addItems([
            "tcg",
            "kvm",
            "hvf",
            "whpx",
            "hax"
        ])
        self.accel_label = QLabel("Acceleration (-accel):")
        config_layout.addWidget(self.accel_label)
        config_layout.addWidget(self.accel_combo)
        self.disk_type_label = QLabel("Disk Type:")
        config_layout.addWidget(self.disk_type_label)
        config_layout.addWidget(self.disk_type_combo)
        self.input_label = QLabel("Input Devices:")
        config_layout.addWidget(self.input_label)
        config_layout.addWidget(self.input_combo)
        self.vga_label = QLabel("Video:")
        config_layout.addWidget(self.vga_label)
        config_layout.addWidget(self.vga_combo)
        self.arch_label = QLabel("Architecture:")
        config_layout.addWidget(self.arch_label)
        config_layout.addWidget(self.arch_combo)
        config_layout.addWidget(QLabel("Machine Type (-machine):"))
        config_layout.addWidget(self.machine_input)

        config_layout.addWidget(QLabel("CPU Model (-cpu):"))
        config_layout.addWidget(self.cpu_model_input)

        config_layout.addWidget(QLabel("BIOS (-bios):"))
        config_layout.addWidget(self.bios_input)
        config_layout.addWidget(self.bios_button)
        self.network_label = QLabel("Network:")
        config_layout.addWidget(self.network_label)
        config_layout.addWidget(self.net_combo)

        config_layout.addWidget(self.snapshot_checkbox)
        config_layout.addLayout(button_layout)
        self.console_label = QLabel("Console output:")
        config_layout.addWidget(self.console_label)
        config_layout.addWidget(self.log_output)
        self.config_button = QPushButton("Configure QEMU Binaries")
        self.config_button.clicked.connect(self.open_config_dialog)
        self.new_vm_button = QPushButton("New VM")
        self.new_vm_button.clicked.connect(self.open_vm_wizard)
        button_layout.addWidget(self.config_button)
        button_layout.addWidget(self.new_vm_button)
        main_layout.addLayout(profile_section, 1)
        main_layout.addLayout(config_layout, 2)
        self.setLayout(main_layout)

    def open_vm_wizard(self):
        wizard = VMWizard(self)
        if wizard.exec():
            config = wizard.get_vm_config()
            QMessageBox.information(self, "VM Configuration", "\n".join(f"{k}: {v}" for k, v in config.items()))
            self.load_vm_config(config)
            

    def load_vm_config(self, config: dict):
        self.arch_combo.setCurrentText(config.get("arch", ""))
        self.ram_input.setText(config.get("ram", ""))
        self.cpu_input.setText(config.get("cpu", ""))
        self.disk_input.setText(config.get("disk", ""))
        self.iso_input.setText(config.get("iso", ""))
        self.bios_input.setText(config.get("bios", ""))
        self.net_combo.setCurrentText(config.get("net", "user"))




    def refresh_profiles(self):
        self.profile_list.clear()
        for profile in profile_manager.list_profiles():
            self.profile_list.addItem(profile)

    def load_selected_profile(self):
        selected = self.profile_list.currentItem()
        if selected:
            profile = profile_manager.load_profile(selected.text())
            if profile:
                self.disk_input.setText(profile.get("disk", ""))
                self.iso_input.setText(profile.get("iso", ""))
                self.ram_input.setText(profile.get("ram", "1024"))
                self.cpu_input.setText(profile.get("cpu", "2"))
                self.machine_input.setText(profile.get("machine", ""))
                vga = profile.get("vga", "none")
                index = self.vga_combo.findText(vga)
                if index != -1:
                    self.vga_combo.setCurrentIndex(index)
                self.cpu_model_input.setText(profile.get("cpu_model", ""))
                self.bios_input.setText(profile.get("bios", ""))
                arch = profile.get("arch", "x86_64 (qemu-system-x86_64)")
                index = self.arch_combo.findText(arch)
                if index != -1:
                    self.arch_combo.setCurrentIndex(index)
                net = profile.get("net", "user (NAT)")
                index = self.net_combo.findText(net)
                if index != -1:
                    self.net_combo.setCurrentIndex(index)
                self.snapshot_checkbox.setChecked(profile.get("snapshot", False))
                self.log_output.append(f"Profilo '{selected.text()}' caricato.\n")
                input_type = profile.get("input", "No input")
                index = self.input_combo.findText(input_type)
                if index != -1:
                    self.input_combo.setCurrentIndex(index)
                usb_bus = profile.get("usb_bus", "No USB")
                index = self.usb_bus_combo.findText(usb_bus)
                if index != -1:
                    self.usb_bus_combo.setCurrentIndex(index)
                disk_type = profile.get("disk_type", "ide")
                index = self.disk_type_combo.findText(disk_type)
                if index != -1:
                    self.disk_type_combo.setCurrentIndex(index)
                accel = profile.get("accel", "tcg")
                index = self.accel_combo.findText(accel)
                if index != -1:
                    self.accel_combo.setCurrentIndex(index)

    def delete_selected_profile(self):
        selected = self.profile_list.currentItem()
        if selected:
            reply = QMessageBox.question(self, "Delete Confirm",
                                         f"Delete Profile '{selected.text()}'?",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                profile_manager.delete_profile(selected.text())
                self.refresh_profiles()
                self.log_output.append(f"Profile '{selected.text()}' deleted.\n")

    def save_as_profile(self):
        name, _ = QFileDialog.getSaveFileName(self, "Save Profile", filter="JSON (*.json)")
        if name:
            if not name.endswith(".json"):
                name += ".json"
            config = {
                "disk": self.disk_input.text(),
                "iso": self.iso_input.text(),
                "ram": self.ram_input.text(),
                "cpu": self.cpu_input.text(),
                "arch": self.arch_combo.currentText(),
                "input": self.input_combo.currentText(),
                "usb_bus": self.usb_bus_combo.currentText(),
                "accel": self.accel_combo.currentText(),
                "disk_type": self.disk_type_combo.currentText(),
                "vga": self.vga_combo.currentText(),
                "net": self.net_combo.currentText(),
                "machine": self.machine_input.text(),
                "cpu_model": self.cpu_model_input.text(),
                "bios": self.bios_input.text(),
                "snapshot": self.snapshot_checkbox.isChecked()
            }
            profile_manager.save_profile(name.split("/")[-1], config)
            self.refresh_profiles()
            self.log_output.append(f"Profile saved as: {name}\n")

    def browse_disk(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Disk Image")
        if file_path:
            self.disk_input.setText(file_path)

    def browse_iso(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select ISO Image")
        if file_path:
            self.iso_input.setText(file_path)

    def launch_vm(self):
        disk = self.disk_input.text()
        iso = self.iso_input.text()
        ram = self.ram_input.text()
        cpu = self.cpu_input.text()
        net = self.net_combo.currentText()
        snapshot = self.snapshot_checkbox.isChecked()
        machine = self.machine_input.text()
        cpu_model = self.cpu_model_input.text()
        bios = self.bios_input.text()
        disk_type = self.disk_type_combo.currentText()


        
        arch_map = {
            "x86_64": "qemu-system-x86_64",
            "aarch64": "qemu-system-aarch64",
            "arm": "qemu-system-arm",
            "riscv64": "qemu-system-riscv64"
        }
        arch_label = self.arch_combo.currentText().split()[0]
        qemu_bin = arch_map.get(arch_label, "qemu-system-x86_64")

        cmd = [qemu_bin, "-m", ram, "-smp", cpu]
        accel = self.accel_combo.currentText()
        if accel:
            cmd += ["-accel", accel]
        usb_bus = self.usb_bus_combo.currentText()
        if "usb-uhci" in usb_bus:
            cmd += ["-device", "usb-uhci"]
        elif "usb-ehci" in usb_bus:
            cmd += ["-device", "usb-ehci"]
        elif "qemu-xhci" in usb_bus:
            cmd += ["-device", "qemu-xhci"]
        input_option = self.input_combo.currentText()
        if "usb-kbd" in input_option:
            cmd += ["-device", "usb-kbd"]
        if "usb-mouse" in input_option:
            cmd += ["-device", "usb-mouse"]
        if "usb-tablet" in input_option:
            cmd += ["-device", "usb-tablet"]
        vga_type = self.vga_combo.currentText()
        if vga_type != "none":
            cmd += ["-device", vga_type]
        if machine:
            cmd += ["-machine", machine]
        if cpu_model:
            cmd += ["-cpu", cpu_model]
        if bios:
            cmd += ["-bios", bios]
        if disk:
            cmd += ["-hda", disk]
        if iso:
            cmd += ["-cdrom", iso, "-boot", "d"]
        if "user" in net:
            cmd += ["-net", "nic", "-net", "user"]
        else:
            cmd += ["-net", "nic", "-net", "bridge"]
        if disk:
            if disk_type == "virtio-blk":
                cmd += ["-drive", f"file={disk},if=none,id=vdisk"]
                cmd += ["-device", "virtio-blk-pci,drive=vdisk"]
            elif disk_type == "usb-storage":
                cmd += ["-drive", f"file={disk},if=none,id=vdisk"]
                cmd += ["-device", "usb-storage,drive=vdisk"]
            else:
                cmd += ["-drive", f"file={disk},if={disk_type}"]


        if snapshot:
            cmd.append("-snapshot")

        self.log_output.append(f"Launch VM with command:\n{' '.join(cmd)}\n")

        self.process = QProcess(self)
        self.process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        self.process.readyReadStandardOutput.connect(self.read_output)
        self.process.start(cmd[0], cmd[1:])

    def read_output(self):
        output = self.process.readAllStandardOutput().data().decode()
        self.log_output.append(output)
    def browse_bios(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select BIOS file")
        if file_path:
            self.bios_input.setText(file_path)
    def update_ui_texts(self):
        # Titolo finestra
        self.setWindowTitle(self.translations["title"])

        # Pulsanti principali
        self.launch_button.setText(self.translations["launch_vm"])
        self.save_button.setText(self.translations["save_profile"])
        self.load_button.setText(self.translations["load_profile"])
        self.delete_button.setText(self.translations["delete_profile"])

        # Etichette dei campi
        self.profile_label.setText(self.translations["profile_label"])
        self.disk_label.setText(self.translations["disk_label"])
        self.disk_button.setText(self.translations["disk_image"])
        self.iso_button.setText(self.translations["iso_image"])
        self.ram_input.setText(self.translations["ram"])
        self.cpu_input.setText(self.translations["cpu"])
        self.arch_label.setText(self.translations["architecture"])
        self.machine_input.setText(self.translations["machine"])
        self.cpu_model_input.setText(self.translations["cpu_model"])
        self.bios_button.setText(self.translations["bios"])
        self.vga_label.setText(self.translations["vga"])
        self.input_label.setText(self.translations["input"])
        self.usb_bus_label.setText(self.translations["usb_bus"])
        self.disk_type_label.setText(self.translations["disk_type"])
        self.accel_label.setText(self.translations["accel"])
        self.network_label.setText(self.translations["network"])
        self.snapshot_checkbox.setText(self.translations["snapshot"])
        self.console_label.setText(self.translations["console_output"])
        self.config_button.setText(self.translations["configure_binaries"])

        # Menu
        self.info_menu.setTitle("Info")
        self.lang_menu.setTitle(self.translations["language"])
        self.about_action.setText(self.translations["about_me"])

        
if __name__ == "__main__":
    from themes import dark_stylesheet
    from themes import light_stylesheet



    app = QApplication(sys.argv)
    
    if is_dark_mode():
        app.setStyleSheet(dark_stylesheet)
    else:
        app.setStyleSheet(light_stylesheet)


    
    


    window = QemuLauncher()
    window.show()
    sys.exit(app.exec())
from ReText import globalSettings
from markups.common import CONFIGURATION_DIR
from os.path import join

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QCheckBox, QDialog, QDialogButtonBox, \
 QGridLayout, QLabel, QLineEdit, QSpinBox

MKD_EXTS_FILE = join(CONFIGURATION_DIR, 'markdown-extensions.txt')

class ConfigDialog(QDialog):
	def __init__(self, parent):
		QDialog.__init__(self, parent)
		self.initConfigOptions()
		self.layout = QGridLayout(self)
		buttonBox = QDialogButtonBox(self)
		buttonBox.setStandardButtons(QDialogButtonBox.Ok |
			QDialogButtonBox.Cancel)
		buttonBox.accepted.connect(self.saveSettings)
		buttonBox.rejected.connect(self.close)
		self.initWidgets()
		self.layout.addWidget(buttonBox, len(self.options), 0, 1, 2)
	
	def initConfigOptions(self):
		# options is a tuple containing (displayname, name) tuples
		self.options = (
			(self.tr('Behavior'), None),
			(self.tr('Automatically save documents'), 'autoSave'),
			(self.tr('Restore window geometry'), 'saveWindowGeometry'),
			(self.tr('Restore live preview state'), 'restorePreviewState'),
			(self.tr('Open external links in ReText window'), 'handleWebLinks'),
			(self.tr('Open unknown files in plain text mode'), 'autoPlainText'),
			(self.tr('Markdown extensions (comma-separated)'), 'markdownExtensions'), (None, 'markdownExtensions'),
			(self.tr('Editor'), None),
			(self.tr('Highlight current line'), 'highlightCurrentLine'),
			(self.tr('Show line numbers'), 'lineNumbersEnabled'),
			(self.tr('Tab key inserts spaces'), 'tabInsertsSpaces'),
			(self.tr('Tabulation width'), 'tabWidth'),
			(self.tr('Display right margin at column'), 'rightMargin'),
			(self.tr('Interface'), None),
			(self.tr('Icon theme name'), 'iconTheme')
			# Ideas for future: styleSheet, editorFont
		)
	
	def initWidgets(self):
		self.configurators = {}
		for index, option in enumerate(self.options):
			displayname, name = option
			if name is None:
				header = QLabel('<h3>%s</h3>' % displayname, self)
				self.layout.addWidget(header, index, 0, 1, 2, Qt.AlignHCenter)
				continue
			if displayname:
				label = QLabel(displayname + ':', self)
			if name == 'markdownExtensions':
				if displayname:
					self.layout.addWidget(label, index, 0, 1, 2)
					continue
				try:
					extsFile = open(MKD_EXTS_FILE)
					value = extsFile.read().rstrip().replace(extsFile.newlines, ', ')
					extsFile.close()
				except Exception:
					value = ''
				self.configurators[name] = QLineEdit(self)
				self.configurators[name].setText(value)
				self.layout.addWidget(self.configurators[name], index, 0, 1, 2)
				continue
			value = getattr(globalSettings, name)
			if isinstance(value, bool):
				self.configurators[name] = QCheckBox(self)
				self.configurators[name].setChecked(value)
			elif isinstance(value, int):
				self.configurators[name] = QSpinBox(self)
				if name == 'tabWidth':
					self.configurators[name].setRange(1, 10)
				else:
					self.configurators[name].setMaximum(100)
				self.configurators[name].setValue(value)
			elif isinstance(value, str):
				self.configurators[name] = QLineEdit(self)
				self.configurators[name].setText(value)
			self.layout.addWidget(label, index, 0)
			self.layout.addWidget(self.configurators[name], index, 1, Qt.AlignRight)

	def saveSettings(self):
		for displayname, name in self.options:
			if name is None or name == 'markdownExtensions':
				continue
			configurator = self.configurators[name]
			if isinstance(configurator, QCheckBox):
				value = configurator.isChecked()
			elif isinstance(configurator, QSpinBox):
				value = configurator.value()
			elif isinstance(configurator, QLineEdit):
				value = configurator.text()
			setattr(globalSettings, name, value)
		self.applySettings()
		self.close()
	
	def applySettings(self):
		QIcon.setThemeName(globalSettings.iconTheme)
		try:
			extsFile = open(MKD_EXTS_FILE, 'w')
			for ext in self.configurators['markdownExtensions'].text().split(','):
				extsFile.write(ext.strip() + '\n')
			extsFile.close()
		except Exception as e:
			print(e)
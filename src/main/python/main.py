from ledgerblue.ecWrapper import PrivateKey
from ledgerblue.comm import getDongle
from ledgerblue.deployed import getDeployedSecretV1, getDeployedSecretV2
from ledgerblue.hexLoader import HexLoader
from ledgerblue.hexLoader import *
from ledgerblue.hexParser import IntelHexParser, IntelHexPrinter
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QApplication, QLabel, QPushButton, QVBoxLayout, QWidget, QMessageBox
from fbs_runtime.application_context.PyQt5 import ApplicationContext
import binascii
import sys
import struct

DEFAULT_ALIGNMENT = 1024
PAGE_ALIGNMENT = 64

dongle = getDongle(True)
appName = "NavCoin"
appVersion = "1.3.17"
appFlags = 0xa50
targetId = 0x31100004

appctxt = ApplicationContext()  
label = QLabel("This app will help you to manage the NavCoin app in your Ledger Nano S.\n\n"
	"Please, connect your Ledger, be sure that it is in the dashboard.\n\n"
	"When you click next, your ledger will ask permission to use an unsafe manager.\n\n"
	"Push the right button until you see Allow unsafe manager and then push both buttons at the same time to allow it.")
label.setAlignment(Qt.AlignCenter)
button = QPushButton("Next")
layout = QVBoxLayout()
layout.addWidget(label)
layout.addWidget(button)
window = QWidget()
window.setLayout(layout)
window.show()

if (sys.version_info.major == 3):
	appName = bytes(appName,'ascii')
if (sys.version_info.major == 2):
	appName = bytes(appName)

privateKey = None
publicKey = None
rootPrivateKey = None
secret = None
loader = None

def click():
	global state, install
	if state == 0:
		if isInstalled():
			label.setText("It looks like the NavCoin app is already installed.\n\nClick next if you want to remove it")
			state = 1
			install = 0
		else:
			label.setText("It looks like the NavCoin app is not installed.\n\nClick next if you want to install it it")
			state = 1
			install = 1
	elif state == 1:
		if install == 1:
			label.setText("Installing...\n\nAccept the operation in the ledger.")
			print("Installing...")
			QTimer.singleShot(1000, installApp)
		else:
			label.setText("Removing...\n\nAccept the operation in the ledger.")
			print("Uninstalling...")
			QTimer.singleShot(1000, remove)


def remove():
	try:
		apps = loader.deleteApp(appName)
	except BaseException as e:
		somethingWrong(e)
	success("App was removed")

def auto_int(x):
	return int(x, 0)

def parse_bip32_path(path, apilevel):
		import struct
		if len(path) == 0:
				return b""
		result = b""
		elements = path.split('/')
		if apilevel >= 5:
			result = result + struct.pack('>B', len(elements))
		for pathElement in elements:
				element = pathElement.split('\'')
				if len(element) == 1:
						result = result + struct.pack(">I", int(element[0]))
				else:
						result = result + struct.pack(">I", 0x80000000 | int(element[0]))
		return result

def string_to_bytes(x):
	import sys
	if sys.version_info.major == 3:
		return bytes(x, 'ascii')
	else:
		return bytes(x)

def installApp():
	try:
		global loader
		apilevel = 10
		fileName = appctxt.get_resource("app.hex")
		appFlags = 0xa50
		parser = IntelHexParser(fileName)
		bootAddr = parser.getBootAddr()
		curveMask = 0x01
		path = b""
		path += struct.pack('>B',curveMask)
		apilevel = 10
		icon = bytearray.fromhex("010000000000ffffffffffffffffff0f870f870787078203c203c041c0e1e0e1e1e1e1ffffffffffff")
		signature = None
		printer = IntelHexPrinter(parser)
		dataSize = 64
		code_length = printer.maxAddr() - printer.minAddr()
		code_length -= dataSize
		installparams = b""
		if (not (appFlags & 2)):
			installparams += encodetlv(BOLOS_TAG_APPNAME, appName)
			installparams += encodetlv(BOLOS_TAG_APPVERSION, string_to_bytes(appVersion))
			installparams += encodetlv(BOLOS_TAG_ICON, bytes(icon))

			param_start = printer.maxAddr()+(PAGE_ALIGNMENT-(dataSize%PAGE_ALIGNMENT))%PAGE_ALIGNMENT
			printer.addArea(param_start, installparams)
			paramsSize = len(installparams)
		else:
			paramsSize = 0

		if bootAddr > printer.minAddr():
			bootAddr -= printer.minAddr()

		loader.createApp(code_length, dataSize, paramsSize, appFlags, bootAddr|1)
		targetVersion = "1.6.0"

		hash = loader.load(0x0, 0xF0, printer, targetId=targetId, targetVersion=targetVersion, doCRC=False) 
		loader.commit(signature)

	except BaseException as e:
		somethingWrong(e)
	success("App was installed {}".format(hash))

def somethingWrong(s):
	QMessageBox.warning(None, "Error", "Something went wrong: {}".format(s))
	sys.exit(-1)

def success(s):
	QMessageBox.information(None, "Ok!", "It worked! {}".format(s))
	sys.exit(-1)

def isInstalled(): 
	try:
		global privateKey, publicKey, rootPrivateKey, secret, loader
		privateKey = PrivateKey()
		publicKey = binascii.hexlify(privateKey.pubkey.serialize(compressed=False))
		rootPrivateKey = privateKey.serialize()
		secret = getDeployedSecretV2(dongle, bytearray.fromhex(rootPrivateKey), targetId)
		cleardata_block_len=None
		if appFlags & 2:
			cleardata_block_len = 16
		loader = HexLoader(dongle, 0xe0, True, secret, cleardata_block_len=cleardata_block_len)
		apps = loader.listApp()
		while len(apps) != 0:
			for a in apps:
				if a["name"] == "NavCoin":
					return True
			apps = loader.listApp(False)
		return False
	except BaseException as e:
		somethingWrong(e)

state = 0
install = 0

button.clicked.connect(click)

exit_code = appctxt.app.exec_()     
sys.exit(exit_code)

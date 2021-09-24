import time
import sys
import vk_api

from PyQt5.QtWidgets import (QApplication, QComboBox, QGridLayout, QGroupBox,
    QHBoxLayout, QVBoxLayout, QLabel, QLineEdit, QPushButton, QRadioButton,
    QSizePolicy, QTextEdit, QWidget, QDialog, QCheckBox)

from LA_GRI_REGIONS import regions
from LA_GRI_OWNER import owner

def captchaHandler(captcha):
	"""
	Gets a captcha image with get_url method,
	then resends request with captcha code 
	"""

	key = input("Enter captcha code {0}: ".format(captcha.get_url())).strip()
	return captcha.try_again(key)

def post(vk=None, group=0, message="", photo=""):

	member = vk.get_api().groups.isMember(group_id=group, user_id=owner)	

	if member == 0:
		vk.get_api().groups.join(group_id=group)	

	return vk.get_api().wall.post(
		owner_id=-group,
		message=message,
		attachments=photo)

def publish(fout=None, vk=None, name="default", message="", photo="", region="", deleter=0):
	
	groups = regions[region][0]
	nbGroups = len(groups)
					
	for counter, group in enumerate(groups, 1):
	
		try:
			res = post(vk=vk, group=group, message=message, photo=photo)
		except:
			print("Couldn't post to group", group, "line", counter, file=fout)
			continue
			
		time.sleep(1)
		print("https://vk.com/wall-", group, '_', res["post_id"], sep='', file=fout)
		print(name, region, ':', "опубликован пост в группе", counter, " из ", nbGroups)

def suggest(fout=None, vk=None, name="default", message="", photo="", region="", deleter=0):
	
	groups = regions[region][1]
	nbGroups = len(groups)
					
	for counter, group in enumerate(groups, 1):
	
		try:
			res = post(vk=vk, group=group, message=message, photo=photo)			
		except:
			print("Couldn't suggest to group", group, "line", counter, file=fout)
			continue
			
		time.sleep(1)
		print("https://vk.com/public", group, sep='', file=fout)
		print(name, region, ':', "предложение сделано в группе", counter, " из ", nbGroups)
	

class WidgetGallery(QDialog):

	def processBoxes(self, fout=None, vk=None, name="default", message="", photo="", caller=None):
		try:
			for box in self.checkBoxes:
				if box.isChecked():
					caller(fout=fout, vk=vk, name=name, message=message, photo=photo, region=box.text())
		except:
			return -1
		return 0

	def buttonClicked(self):
		
		login = self.loginLineEdit.text()
		password = self.passwordLineEdit.text()
		name = self.nameLineEdit.text()
		message = self.postText.toPlainText()
		photo = "photo" + str(owner) + "_" + self.photoLineEdit.text()
		
		vk = vk_api.VkApi(login, password, captcha_handler=captchaHandler)
		
		try:
			vk.auth()
		except vk_api.AuthError as error_msg:
			print(error_msg)
			return
		
		outputFile = name + ".txt"
		with open(outputFile, 'a') as f:
			
			print("----------", file=f)
			
			
			print(name, "опубликовано:", file=f)	
			if self.processBoxes(fout=f, vk=vk, name=name, message=message, photo=photo, caller=publish) < 0:
				f.close()
				return
			
			
			if self.allowModeration.isChecked():
				print(name, "предложено:", file=f)		
				if self.processBoxes(fout=f, vk=vk, name=name, message=message, photo=photo, caller=suggest) < 0:
					f.close()
					return
			
		
		f.close()
		

	def createTopLayout(self):
	
		self.loginLineEdit = QLineEdit("")
	
		loginLabel = QLabel("&Логин ВК:")
		loginLabel.setBuddy(self.loginLineEdit)

		self.passwordLineEdit = QLineEdit("")
		self.passwordLineEdit.setEchoMode(QLineEdit.Password)
		passwordLabel = QLabel("&Пароль ВК:")
		passwordLabel.setBuddy(self.passwordLineEdit)
		
		layout = QHBoxLayout()
		layout.addWidget(loginLabel)
		layout.addWidget(self.loginLineEdit)
		layout.addStretch(1)
		layout.addWidget(passwordLabel)
		layout.addWidget(self.passwordLineEdit)
		
		return layout
		
	def createBottomLayout(self):
		
		publishButton = QPushButton("Опубликовать")
		publishButton.clicked.connect(self.buttonClicked)
		
		self.photoLineEdit = QLineEdit("")
		photoLabel = QLabel("&Идентификатор фото:")
		photoLabel.setBuddy(self.photoLineEdit)

		layout = QHBoxLayout()
		layout.addWidget(publishButton)
		layout.addStretch(1)
		layout.addWidget(photoLabel)
		layout.addWidget(self.photoLineEdit)
		
		return layout


	def createLeftBox(self):
	
		box = QGroupBox()

		layout = QVBoxLayout()
		
		self.checkBoxes = []
		
		for region in regions.keys():
			checkBox = QCheckBox(region)
			layout.addWidget(checkBox)
			self.checkBoxes.append(checkBox)
			
		self.allowModeration = QRadioButton("МОДЕРАЦИЯ")
		layout.addWidget(self.allowModeration)
		
		layout.addStretch(1)
		
		box.setLayout(layout)
		
		return box
		
	def createRightBox(self):
	
		box = QGroupBox()
	
		self.nameLineEdit = QLineEdit("")
		nameLabel = QLabel("&Имя пропавшего:")
		nameLabel.setBuddy(self.nameLineEdit)

		topLayout = QHBoxLayout()
		topLayout.addWidget(nameLabel)
		topLayout.addWidget(self.nameLineEdit)
	
		self.postText = QTextEdit()
		self.postText.setPlainText("Введите текст сообщения о пропавшем\n")
		
		bottomLayout = QHBoxLayout()
		bottomLayout.setContentsMargins(5, 5, 5, 5)
		bottomLayout.addWidget(self.postText)

		layout = QVBoxLayout()
		layout.addLayout(topLayout)
		layout.addLayout(bottomLayout)
		layout.addStretch(1)
		
		box.setLayout(layout)
		
		return box	
	
	def __init__(self, parent=None):
	
		super(WidgetGallery, self).__init__(parent)
		self.originalPalette = QApplication.palette()

		layout = QGridLayout()
		layout.addLayout(self.createTopLayout(), 0, 0, 1, 2)
		layout.addLayout(self.createBottomLayout(), 1, 0, 1, 2)
		layout.addWidget(self.createLeftBox(), 2, 0)
		layout.addWidget(self.createRightBox(), 2, 1)
		layout.setRowStretch(0, 1)
		layout.setRowStretch(1, 2)
		layout.setColumnStretch(0, 1)
		layout.setColumnStretch(1, 1)
		
		self.setLayout(layout)
		self.setWindowTitle("Робот LizaAlert")
	
if __name__ == '__main__':
	app = QApplication(sys.argv)
	gallery = WidgetGallery()
	gallery.show()
	sys.exit(app.exec_()) 
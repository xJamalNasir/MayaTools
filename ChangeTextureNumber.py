# !python2.7
# -*- coding: utf-8 -*-
# コーディング: utf-8
# ____________________________________________________________________________________________
from __future__ import absolute_import, division, generators, print_function, unicode_literals
from future_builtins import *
import maya.cmds as cmds
import maya.mel as mel
import glob
import re
# Folder name is different. Has two different numbering patterns
# two types of textures: regular and cut
# Before 01, 02. Now:  00n, 10n ...
# IMP - This time theres some empty textures in hypershade so you dont have to change all textures
# Folder path doesn't have the proj name in it so that program isn't necessary
# IMP - everything has two textures so prepare code to take in multiple textures even if currently there's one
# ch is accessory - dont use ce - cb is costume
# Use one button this time but if it goes over 4 add another button. Button isnt necerray, use in CRTools

# テクスチャを変更する

def ML_CTN_changeTexture():
    _top = ["cb", "ch"]

    # テクスチャナンバー取得
    for _texture in cmds.ls(et="file"):
        _fullName = cmds.getAttr("{}.fileTextureName".format(_texture))
        _fullName = '/'.join(_fullName.split('\\'))
        _texName = _fullName.split("/")[-1] 

       # cb,ch_ss以外は処理しない
        if not re.match('(%s)_ss\d' % "|".join(_top), _texName):
            continue

        # get texture number n01
        _texNumber = _texName[5:6]
        _texTopName = _texName[:2]
        
        # change texture number
        _texNumber = not int(_texNumber)

        # change full name
        _fullName = re.sub("(%s)_ss[0-1]" % "|".join(_top), "%s_ss%d" % (_texTopName, int(_texNumber)), _fullName)
        
        cmds.setAttr("{}.fileTextureName".format(_texture), _fullName, type="string")

        print(_fullName)
        
    mel.eval('print("衣装テクスチャを変えました。\\n")')


ML_CTN_changeTexture()

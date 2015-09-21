import os.path


_EGG_PYTHON_TAG_BLACK_LIST = {
    'EPDDocs-1.0-1.egg': {
        '5c3ad0ca9e1bd26b8d074cf80c06380c424515e9ae6e59514470846107e60519':
        'py27'
    },
    'EPDIndex-1.0-1.egg': {
        'a46d8a17e56ac7dced58adec5207c46a629c1583ebcc41b4d893e9f7f3066e2d':
        'py27'
    },
    'EPDIndex-1.1-1.egg': {
        '07d8e55d1d6930eaad0d4dc565d4320ca4d4ed8ade5c8910f3162a4e8a1c045c':
        'py27'
    },
    'EPDIndex-1.2-1.egg': {
        'd5a4f69be18c170d13bafe3850c44973900a8a0df621e1f4b9560b2b62229ce1':
        'py27'
    },
    'Examples-7.1-1.egg': {
        'c4aa67cec4ab854f57c6cbaaee5dc1ec8f867bb2563fb165f6decec6399a4e75':
        'py27'
    },
    'Examples-7.1-2.egg': {
        '13ecc980ed6b0b1f350b94ea9836c093a8459acf634b2c59ef7fd86e3318c0ab':
        'py27'
    },
    'Examples-7.2-1.egg': {
        '1ce34c22cca8b4dcf164b2c4fe34424ed0c7f706a9c2e9ce1801bf8a746dbffa':
        'py27'
    },
    'Examples-7.3-1.egg': {
        'af7ccfe1198625e56f7717dba4a15c32405499772d581fc67cd86ad18017cd39':
        'py27'
    },
    'MKL-10.2-1.egg': {
        '0e799bb5e7afd4d9e086d3af075c8c5735c9598208dc2ee92df6f29ead1a8d03':
        'py27',
        '8ae85227cb55b539923a3ed96bd63f91314fa4d852966f44989364aab2f4b2a9':
        'py27'
    },
    'MKL-10.2-2.egg': {
        '019a74518dfea53ace5a70f3f9eeb4943b8c55883eb5daeefb1343fa368f3683':
        'py27',
        '0207aa974b5c3e20a2e9a54caa04895ac872e55e2b2ebe8e18066db4bec3647e':
        'py27'
    },
    'MKL-10.3-1.egg': {
        '3be3e3a0b084f064c5aa6c071bdb62ab812a479ebc6d97125b0c0495707205bb':
        'py27',
        '55e90b84188ff41ce641aa75daf462981ab29f924fe2e4840949aa1e8235acd5':
        'py27'
    },
    'PyQt-4.10.3-1.egg': {
        'd058ef7737bf7dfced53d71ac9c623e3849598c90cd186e1a30361a4f12df6b5':
        'py27'
    },
    'PyQt-4.11.0-1.egg': {
        '4aab7e47d3cce7d10dfd4f93a4008160fd7f6f8f72b081e6649d5576cec0dbdc':
        'py27'
    },
    'PySide-1.0.3-1.egg': {
        '5af973a78c53bfa4fe843992bc86207d5c945b06f7df576e64463a743a558fb1':
        'py27',
        '87d3ac97c4ae6688bce24b00b536798b07065af3b1b9503d8d4e920df520f878':
        'py27'
    },
    'PySide-1.0.3-2.egg': {
        'b35e240502b35c5ef89b1578a8cd9cd067a29ea29839225928297a08888a0756':
        'py27',
        'becc93f4452c55e28b6c1e78529cae37e686c1b7a8adce151d319127c839e79a':
        'py27'
    },
    'PySide-1.0.5-1.egg': {
        '0e411b4236a3b950542d673ef8d2700c480c1112e320c76f805d57947446098e':
        'py27',
        '4e571d9bbb967f9fd007da459521dfda838f0414dbcc171128f579cf727e6ac4':
        'py27'
    },
    'PySide-1.0.7-1.egg': {
        '5751220a0387b5e301cfd75b2d71c982860e06dccd9f6092d36db7561f3a4e0d':
        'py27'
    },
    'PySide-1.0.8-1.egg': {
        '9f28e28cd44d9f96cd9584c1a00796bcd1351b179a0b16e91fa936d6f34defba':
        'py27'
    },
    'PySide-1.0.8-2.egg': {
        'a31cdff5ed58e1372a7420b39df6905b16f4dba000a4b2806ec3801bb22f8946':
        'py27'
    },
    'PySide-1.0.9-1.egg': {
        '17f094b5a3b3b41b0c89318fdff9d3333abb9a2960eabcf5eb0dc9844f0c1fa1':
        'py27'
    },
    'PySide-1.1.0-1.egg': {
        '0e516e51f6777daea4a245a1a3a2f3678be973184e5e6bda4e1fd0de44e6166c':
        'py27'
    },
    'PySide-1.1.0-2.egg': {
        '4cb34144dc51c469dd35607478bd4df46741815c92f4b7097afcb26f20c0ed36':
        'py27',
        'e007885c53ec59aa8677df8735546e03081d00d7d267e17178286366f10e4666':
        'py27'
    },
    'PySide-1.1.0-3.egg': {
        '08205d8182a759d10ebedfa67fc3238a5328ba895387af48982a4f97c29eb71a':
        'py27',
        '557140ee925f6ad46904f8d6a2526095f92a11ccdcd373636a308146cfe1e158':
        'py27'
    },
    'PySide-1.2.1-1.egg': {
        '2e5872f321844aace41f2c05169a0a73050c11ccbc8acad785142cd2aa495692':
        'py27',
        '3d187d3e183d6a1566a0cc203cbb1884132c11f74cb3147cff4d9ff4a842c7b5':
        'py27'
    },
    'PythonDoc-2.7.3-1.egg': {
        '585f98d92a35efa7e0b0f0ac01eed464f94a567d3d8929a532651f9c3f66d5ec':
        'py27'
    },
    'agw-0.9.1-1.egg': {
        'fd79fe6dc3c4ec6355f6f0b3dfe5710bca50e1d450d73267a4214f5786df34d1':
        'py27'
    },
    'basemap_ld-1.0.1-1.egg': {
        '7c7a7af2aab55df7927549901b408841fda1763ad9f9f26f277fcc4dd6ba8e13':
        'py27'
    },
    'basemap_ld-1.0.2-1.egg': {
        'b619a0c32958cb9e197f3c85ff85a9de16f42b0eba46782ca5db5317dc1268e4':
        'py27'
    },
    'basemap_ld-1.0.6-1.egg': {
        '5e279e940ac5b8154d9d1065cdc81b02b30942a9c6a2639ab9bad378f3befb6c':
        'py27'
    },
    'basemap_ld-1.0.7-1.egg': {
        '2d883c1d90474d62057d99cbc1eaa3895d4bc0b805200035a425f200113bca75':
        'py27'
    },
    'casuarius-1.0-1.egg': {
        '3634bd18c47287bafec070be328010e49dfab41e4bab9dd5cb5e9b5873393506':
        'py27'
    },
    'casuarius-1.0b1-1.egg': {
        'b8fdc341fe3cf6fa5d291645dc7ceec894e4a215b6153ba21a24ad64a4633016':
        'py27'
    },
    'casuarius-1.1-1.egg': {
        '283d0851c5e4dcf07264547a43900fe2b3d075fcb31f850ad48bdfcc38fdf535':
        'py27'
    },
    'casuarius-1.1-2.egg': {
        'f57ad4f6c31dd2c5d5bed0afde2de0aaa2929a791d18f4a255f35e12f296add4':
        'py27'
    },
    'casuarius-1.1-3.egg': {
        '264428d6db5588ee81d9ec8e3822ab4f7f7e4b4b8684ee5001f72eb02e8c0e1f':
        'py27'
    },
    'doclinks-7.1-1.egg': {
        'f2ab7822e36e43eaeff098337b5fbdcc0821b76088ff6c018162e17effce0047':
        'py27'
    },
    'doclinks-7.1-2.egg': {
        'bb8ef13044fc1da01473c756aa37ce1951c654ac28c72e4501f96787d1877908':
        'py27'
    },
    'doclinks-7.2-1.egg': {
        'f9938be4436cdca0ab0ba558c108631d262a7a5fbdbf05ecc88122563d9b9f61':
        'py27'
    },
    'doclinks-7.2-2.egg': {
        'e3cda2045f3f928c07f19299e511083f2c7aa240a28285061f0fc8f6442a4fcb':
        'py27'
    },
    'doclinks-7.3-1.egg': {
        'c998ec0d824b0a3ede8412f6c4e0cdcf59aa47a5e8174535c565d7e841b88070':
        'py27'
    },
    'enstaller-4.5.0-1.egg': {
        '30667f62941dbcbdb1ac9134d2b084ce797c4e1babf0b6186db7c21114edf6f6':
        'py27'
    },
    'enstaller-4.5.1-1.egg': {
        '028af870081650fd710fbf49a68de1114c6a342ec3df8683c861a43ad6c4ead9':
        'py27'
    },
    'enstaller-4.5.2-1.egg': {
        '9dd05422ae5b9fdceb58963ea4b16600604e7305186ad6e85a7988e7dcb2173f':
        'py27'
    },
    'enstaller-4.5.3-1.egg': {
        'c0cdfc2f25c6392352ba3ae6afa52bf652a75926499d01b1c141ce8de85d8325':
        'py27'
    },
    'kiwisolver-0.1.2-1.egg': {
        '03ec49eea3ba16b3fc36f1cff5a2f944909b18e1b41fc84a1c47fc5b8bcac781':
        'py27'
    },
    'opencv-2.4.5-2.egg': {
        '678e5a7e07eb52ac14f1c6eb8df0963756f4ceb438f740b4734d74da133b12e1':
        'py27'
    },
    'opencv-2.4.5-3.egg': {
        '5ba2877340c0c5f94c280d934dfb96a768de37b8540ce46af8633a61fc05f096':
        'py27'
    },
    'pyodbc-2.1.8-1.egg': {
        '74440b9d2c3ae34f0fe559d8f27bc2db1f3c5289543ef84223510ec652f2b79a':
        'py27'
    },
    'pyodbc-3.0.6-1.egg': {
        '0327d096765dd08937421d699b007450382bc2e8c4ce473e6c6b5e7c78a02a31':
        'py27'
    },
    'pyside-1.0.0rc1-1.egg': {
        'ed90e9b6c83d4f9fb0a7db2a5fc508639ac549a5c3d0bb4aabfd10b5f81a7601':
        'py27'
    },
    'shiboken-1.2.1-2.egg': {
        '3d33f6f9864d1890ac79ff56671a9a0565ab2464916a32fb0feadfe0ceb346d7':
        'py27'
    },
    'sip-4.15.3-1.egg': {
        '28325a7adae018a85df3a8981b7a7f5aa8c30229c28952577f77bb72b8b2dd7b':
        'py27'
    },
    'sip-4.16.1-1.egg': {
        '01a6e5041649ec3093492ffa44f809f3d3baabb75aca8eaec6160fddc66bc2d5':
        'py27'
    },
    'ujson-1.33.0-1.egg': {
        '80cc7357fd8126eae2b1610de858c671cc56e171d8f0c737ffed1901b27ff1a7':
        'py27'
    }
}


# (egg sha256) -> (epd platform string) mapping
EGG_PYTHON_TAG_BLACK_LIST = dict(
    (checksum, python_tag)
    for egg in _EGG_PYTHON_TAG_BLACK_LIST.values()
    for checksum, python_tag in egg.items()
)


def may_be_in_python_tag_blacklist(path):
    """ Returns True if the given egg path may be in the python tag blacklist.
    """
    return os.path.basename(path) in _EGG_PYTHON_TAG_BLACK_LIST

from PyInstaller.utils.hooks import collect_data_files
from PyInstaller.utils.hooks import collect_submodules
from PyInstaller.utils.hooks import copy_metadata

datas = copy_metadata('kuryr_rancher')
datas += collect_data_files('kuryr_rancher')


hiddenimports = collect_submodules('kuryr_rancher.cni.binding')

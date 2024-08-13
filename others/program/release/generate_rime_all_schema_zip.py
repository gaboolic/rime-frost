import zipfile  
import os  
  
def zip_folders_and_files(zip_name, folders, files):  
    """  
    将指定的多个文件夹和文件打包成一个ZIP文件。  
  
    :param zip_name: 输出的ZIP文件名  
    :param folders: 要打包的文件夹名列表  
    :param files: 要打包的文件名列表  
    """  
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:  
        # 添加文件夹  
        for folder in folders:  
            for root, dirs, files_in_folder in os.walk(folder):  
                for file in files_in_folder:  
                    file_path = os.path.join(root, file)  
                    arcname = os.path.relpath(file_path, os.path.dirname(folder))  
                    zipf.write(file_path, arcname)  
          
        # 添加文件  
        for file in files:  
            if os.path.isfile(file):  
                zipf.write(file, os.path.basename(file))  
  
# todo
remove_list = ['cn_dicts_dazhu','others','program','recipes','./','build','sync','.DS_Store','frost_dict_for_fcitx5.txt']
folders = []
# 使用 os 模块中的 listdir 函数列出指定文件夹中的所有文件和子目录
files = []
file_names = os.listdir("./")
# 打印出所有找到的文件名
for file_name in file_names:
    print(file_name)
    if file_name not in remove_list and '.userdb' not in file_name and '.git' not in file_name and '.idea' not in file_name and '.zip' not in file_name and 'custom' not in file_name:
        if os.path.isdir(os.path.join("./", file_name)):
            folders.append(file_name)
        else:
            files.append(file_name)

print(folders)
print(files)

zip_folders_and_files('rime-frost-schemas.zip', folders, files)
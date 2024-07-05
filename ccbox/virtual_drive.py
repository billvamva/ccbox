from typing import Union, List, Dict, Optional, Any, ClassVar, Callable
from dataclasses import dataclass, field
from itertools import count
import os

from ccbox.storage_handler import StorageHandler, AzureStorageHandler
from ccbox.helper import NamedTextIOWrapper

@dataclass
class FileSystemObject:
        _name: str
        folders: Dict[str, "Folder"] = field(default_factory=lambda: {})
        contents: List[Union[object, "Folder"]] = field(default_factory=list)
        metadata:Dict[str, Any] = field(default_factory=lambda: {})

        def add_folder(self, name: str, folder_obj: Optional["Folder"] = None) -> Union["Folder", None]:
                for item in self.contents:
                        if type(item).__name__ == "Folder":
                                if item._name == name:
                                        raise Exception(f"A folder with the name {name} already exists.")
                                        return
                if folder_obj:
                        curr_folder = folder_obj
                else:
                        curr_folder = Folder(name, parent_dir=self)
                self.contents.append(curr_folder)
                self.folders[curr_folder._name] = curr_folder
                return curr_folder
        
        def add_file(self, obj: object) -> None:
                self.contents.append(obj)
        
        def change_directory(self, folder_name) -> "FileSystemObject":
                curr_directory = None
                if folder_name in self.folders:
                        curr_directory = self.folders.get(folder_name)
                        return curr_directory
                elif folder_name == "..":
                        try:
                                curr_directory = self.parent_dir
                                return curr_directory
                        except:
                                print("In root directory.")
                else: 
                        print("Invalid Folder name.")

        def mount_directory(self, dir_path:str) -> None:
                try: 
                        dir_list = os.listdir(dir_path)
                except:
                        raise ValueError("Invalid Path")
                        return

                mount_folder = self.add_folder(os.path.basename(dir_path))

                for item in dir_list:
                        if os.path.isdir(dir_path + "/" + item):
                                mount_folder.mount_directory(dir_path + "/" + item)
                        elif os.path.isfile(dir_path + "/" + item):
                                with open(dir_path + "/" + item) as new_file:
                                        new_file = NamedTextIOWrapper(new_file, item)
                                        mount_folder.contents.append(new_file)

        def to_dict(self) -> dict:
                return {
                "_name": self._name,
                "folders": {name: f.to_dict() for name, f in self.folders.items()},
                "contents": [f.to_dict() if isinstance(f, Folder) else str(f) for f in self.contents],
                "metadata": self.metadata
                }
        
        @classmethod
        def from_dict(cls, data: dict) -> "FileSystemObject":
                obj = cls(_name=data["_name"])
                obj.contents = [Folder.from_dict(f) if isinstance(f, dict) else f for f in data["contents"]]
                obj.folders = {name: Folder.from_dict(f) for name, f in data["folders"].items()}
                obj.metadata = data["metadata"]
                return obj

        def __repr__(self):
                return f'{type(self).__name__}(\'{self._name}\', {self.folders}, {super.contents}, {self.metadata})'

@dataclass(kw_only=True)
class Folder(FileSystemObject):
        parent_dir: Union["Virtual_Drive", "Folder"]

        def show_contents(self) -> None:
                print(f"dir:{self._name}")
                print("\t")
                for item in self.contents:
                        if item == self.parent_dir:
                                print("..")
                        elif type(item).__name__ == Folder:
                                print(f"{item._name}/")
                        else:
                                print(item._name)
        

        @classmethod
        def from_dict(cls, data: dict, parent_dir=None) -> "Folder":
                folder = Folder(_name=data["_name"], parent_dir=parent_dir)
                folder.contents = [cls.from_dict(data=f, parent_dir=folder) if isinstance(f, dict) else f for f in data["contents"]]
                folder.folders = {name: cls.from_dict(data=f, parent_dir=folder) for name, f in data["folders"].items()}
                folder.metadata = data["metadata"]
                return folder



@dataclass(kw_only=True)
class Virtual_Drive(FileSystemObject):
        _name: str = "VD"
        id_counter: count = count()
        _id: int =  field(default_factory=lambda: next(Virtual_Drive.id_counter))
        _from_dict: bool = False
        storage_handler: StorageHandler = None

        def __post_init__(self):
                if not self._from_dict:
                        default_folder = Folder(_name="default", parent_dir=self)
                        self.folders['default'] = default_folder 
                        self.contents.append(default_folder)
        
        
        def show_contents(self) -> None:
                print(f"dir:{self._name}")
                print("\t")
                for item in self.contents:
                        if type(item).__name__ == Folder:
                                print(f"{item._name}/")
                        else:
                                print(item._name)
        
        
        def upload_contents(self) -> None:
                container_name = self.storage_handler.container_name
                for item in self.contents:
                        if isinstance(item, Folder):
                                self.upload_folder(item, container_name)
                        else:
                                self.upload_file(item, container_name)

        def upload_folder(self, folder: Folder, container_name: str, parent_name: Optional[str] = None) -> None:
                # Create a blob for the folder and upload its contents recursively
                if parent_name:
                        folder_path = f"{parent_name}/{folder._name}"
                else:
                        folder_path = folder._name
                folder_path_name = f"{folder_path}/"
                self.storage_handler.upload_from_bytes(
                container_name, folder_path_name, b""
                )  # Create a blob for the folder
                for item in folder.contents:
                        if isinstance(item, Folder):
                                self.upload_folder(item, container_name, folder_path)
                        else:
                                self.upload_file(item, container_name, folder_path)

        def upload_file(self, file_obj: object, container_name: str, folder_name: Optional[str] = None) -> None:
                # Upload a file to Azure Blob Storage
                file_name = file_obj._name if hasattr(file_obj, "_name") else ""
                blob_name = f"{folder_name}/{file_name}" if folder_name else file_name
                with open(file_obj.name, "rb") as f:
                        self.storage_handler.upload_from_bytes(container_name, blob_name, f.read())

        def add_remote(self, storage_handler: StorageHandler) -> None:
                self.storage_handler = storage_handler
        
        def save_to_remote(self) -> None:
                if self.storage_handler:
                        object_name = f'virtual_drive_{self._id}.json'
                        vd_dict = self.to_dict()
                        self.storage_handler.upload_json(vd_dict, object_name)
                else:
                        print("Storage handler not configured.")

        def load_from_remote(self, object_name: str) -> None:
                if self.storage_handler:
                        vd_dict = self.storage_handler.download_json(object_name)
                        loaded_vd = Virtual_Drive.from_dict(vd_dict)
                        self.__dict__.update(loaded_vd.__dict__)
                else:
                        print("Storage handler not configured.")
        
        def to_dict(self) -> dict:
                return {
                "_id": self._id,
                "_name": self._name,
                "folders": {name: f.to_dict() for name, f in self.folders.items()},
                "contents": [f.to_dict() if isinstance(f, Folder) else str(f) for f in self.contents],
                "metadata": self.metadata,
                "storage_handler": self.storage_handler.to_dict()
                }
        
        @classmethod
        def from_dict(cls, data:dict) -> "Virtual_Drive":
                obj = super().from_dict(data)
                obj.add_remote(storage_handler=AzureStorageHandler.from_dict({
                        "account_url" : data["storage_handler"]["account_url"],
                        "container_name" : data["storage_handler"]["container_name"]
                }))
                return obj

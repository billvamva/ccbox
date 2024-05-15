from typing import Union, List, Dict, Optional, Any, ClassVar, Callable
from dataclasses import dataclass, field
from itertools import count
import os

@dataclass
class FileSystemObject:
        name: str
        folders: Dict[str, "Folder"] = field(default_factory=lambda: {})
        contents: List[Union[object, "Folder"]] = field(default_factory=list)
        metadata:Dict[str, Any] = field(default_factory=lambda: {})

        def add_folder(self, name: str, folder_obj: Optional["Folder"] = None) -> Union["Folder", None]:
                for item in self.contents:
                        if type(item).__name__ == Folder:
                                if item.name == name:
                                        raise Exception(f"A folder with the name {name} already exists.")
                                        return
                if folder_obj:
                        curr_folder = folder_obj
                else:
                        curr_folder = Folder(name, parent_dir=self)
                self.contents.append(curr_folder)
                self.folders[curr_folder.name] = curr_folder
                return curr_folder
        
        def add_file(self, obj: object) -> None:
                self.contents.append(obj)
        
        def change_directory(self, folder_name):
                if folder_name in curr_directory.folders:
                        curr_directory = curr_directory.folders.get(folder_name)
                elif folder_name == "..":
                        try:
                                curr_directory = curr_directory.parent_dir
                        except:
                                print("In root directory.")
                else: 
                        print("Invalid Folder name.")

        def mount_directory(self, dir_path:str):
                try: 
                        dir_list = os.listdir(dir_path)
                except:
                        raise ValueError("Invalid Path")
                        return

                mount_folder = self.add_folder(os.path.basename(dir_path))

                for item in dir_list:
                        if os.path.isdir(dir_path + "/" + item):
                                new_folder = mount_folder.add_folder(item)
                                new_folder.mount_directory(dir_path + "/" + item)
                        elif os.path.isfile(dir_path + "/" + item):
                                new_file = open(dir_path + "/" + item)
                                mount_folder.contents.append(new_file)

        def __repr__(self):
                return f'FSO(\'{self.name}\', {self.folders}, {self.metadata})'

@dataclass(kw_only=True)
class Folder(FileSystemObject):
        parent_dir: Union["Virtual_Drive", "Folder"]

        def show_contents(self) -> None:
                print(f"dir:{self.name}")
                print("\t")
                for item in self.contents:
                        if item == self.parent_dir:
                                print("..")
                        elif type(item).__name__ == Folder:
                                print(f"/{item.name}")
                        else:
                                print(os.path.basename(item.name))
        
        def to_dict(self) -> dict:
                return {
                "name": self.name,
                "folders": {name: f.to_dict() for name, f in self.folders.items()},
                "contents": [f.to_dict() if isinstance(f, Folder) else str(f) for f in self.contents],
                "metadata": self.metadata
                }

        @classmethod
        def from_dict(cls, data: dict, parent_dir=None) -> "Folder":
                folder = Folder(name=data["name"], parent_dir=parent_dir)
                folder.contents = [cls.from_dict(datal=f, parent_dir=folder) if isinstance(f, dict) else f for f in data["contents"]]
                folder.folders = {name: cls.from_dict(data=f, parent_dir=folder) for name, f in data["folders"].items()}
                folder.metadata = data["metadata"]
                return folder



@dataclass(kw_only=True)
class Virtual_Drive(FileSystemObject):
        name: str = "VD"
        id_counter: count = count()
        virtual_drive_id: int =  field(default_factory=lambda: next(Virtual_Drive.id_counter))
        locked: bool = field(default=True)
        _from_dict: bool = False
        user_obj: "User" = None
        _save_method: Callable = None

        def __post_init__(self):
                if not self._from_dict:
                        default_folder = Folder(name="default", parent_dir=self)
                        self.folders['default'] = default_folder 
                        self.contents.append(default_folder)
        
        
        def show_contents(self) -> None:
                print(f"dir:{self.name}")
                print("\t")
                for item in self.contents:
                        if type(item).__name__ == Folder:
                                print(f"/{item.name}")
                        else:
                                print(os.path.basename(item.name))
        
        def unlock(self) -> None:
                self.locked = False
        
        def lock(self) -> None:
                self.locked = True

        def add_save_callable_attr(curr_user: "User", _save_method: Callable) -> None:
                self.user_obj = curr_user
                self._save_method = _save_method
        
        def _save(self):
                self._save_method(self.user_obj)
        
        def to_dict(self) -> dict:
                return {
                "virtual_drive_id": self.virtual_drive_id,
                "locked": self.locked,
                "folders": {name: f.to_dict() for name, f in self.folders.items()},
                "contents": [f.to_dict() if isinstance(f, Folder) else str(f) for f in self.contents],
                }
        
        def __repr__(self):
                return f'Virtual Drive(\'{self.virtual_drive_id}\', {self.folders})'



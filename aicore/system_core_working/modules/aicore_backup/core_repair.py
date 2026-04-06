import shutil
import os


class CoreRepair:

    BACKUP = "/root/aicore_backup"

    def repair(self, file):

        src = os.path.join(self.BACKUP, file)
        dst = os.path.join("/root/aicore", file)

        if not os.path.exists(src):
            return {
                "status": "failed",
                "reason": "no_backup"
            }

        shutil.copy(src, dst)

        return {
            "status": "restored",
            "file": file
        }

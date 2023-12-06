from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from urllib.parse import quote  # 正确导入quote函数
import os

from starlette.responses import FileResponse

app = FastAPI()

# 用于存储上传文件的路径
upload_dir = os.path.expanduser("~/uploads")

@app.post("/upload/")
async def upload_file(file: UploadFile):
    try:
        # 如果上传目录不存在，创建它
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)

        # 构建文件的完整路径
        file_path = os.path.join(upload_dir, file.filename)

        # 将上传的文件写入到目标路径
        with open(file_path, "wb") as f:
            f.write(file.file.read())

        return JSONResponse(content={"message": "文件上传成功"}, status_code=200)
    except Exception as e:
        return JSONResponse(content={"message": f"文件上传失败：{str(e)}"}, status_code=500)



# 用于存储下载文件的路径
download_dir = os.path.expanduser("~/Downloads")
1
@app.get("/download/{file_name}")
async def download_file(file_name: str):
    try:
        # 构建文件的完整路径
        file_path = os.path.join(download_dir, file_name)

        # 检查文件是否存在
        if not os.path.exists(file_path):
            return {"message": "文件不存在"}, 404

        # 对文件名进行URL编码
        encoded_file_name = quote(file_name)

        # 返回文件作为响应，并设置Content-Disposition头部
        headers = {"Content-Disposition": f'attachment; filename="{encoded_file_name}"'}
        return FileResponse(file_path, headers=headers)
    except Exception as e:
        return {"message": f"下载文件失败：{str(e)}"}
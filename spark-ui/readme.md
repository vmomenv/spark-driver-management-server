在用户主目录部署node.js
`vim .profile`
```bash
export NODE_HOME=/home/momen/node-v18.18.0-linux-x64
export PATH=$PATH:$NODE_HOME/bin 
export NODE_PATH=$NODE_HOME/lib/node_modules
```
写好以后，使用
`source .profile`应用修改

查看是否生效
```bash
momen@momen-PC:~$ node -v
v18.18.0
```
改为国内淘宝源
`npm config set registry https://registry.npm.taobao.org`

查看修改是否成功
```bash
npm config get registry
输出：https://registry.npm.taobao.org/
```
安装vue
`npm install --global @vue/cli`
安装element-ui
`npm install element-ui`
### minikube command
 - ``minikube start --driver=docker > /dev/null 2>&1 &``
 - ``minikube status``
 - ``minikube start --driver=docker``

### kubectle 成功紀錄
 - 抓取docker 映像檔案到 minikube 裡面
 - minikube image load flask-book-app  
 - kubectl -f flask-pod.yaml --(pod)
 - kubectl -f flask-service.yaml --(service)
 - kubectl minikube service flask-service -- or
 - kubectl minikube service flask-service --url

 - 不採用 yaml 建立
 - kubectl run mypod --image=flask-book-app --image-pull-policy=Never --port=5010
 - kubectl port-forward pod/mypod 5010:5010


### k8s kubctl command 

 - kubectl start 
 - kubectl apply -f flask-deployment.yaml
 - kubectl apply -f service.yaml

 - 
 - list all pods
 - kubectl get pods
 - kubectl scale deployment flask-app --replicas=0
 - kubectl describe pod

|***步驟***|***	指令 ***|
|----------|-----------|
|部署 Flask 服務|	kubectl apply -f flask-service.yaml|
|檢查 Service 是否啟動|	kubectl get services|
|測試 Flask 服務（Minikube）|	minikube service flask-service|
|測試 Flask 服務（手動）|	curl http://$(minikube ip):30080|
|測試 Flask 服務（內部 Pod）|	kubectl exec -it <pod-name> -- curl http://flask-service:5000|
|停止 Service	|kubectl delete service flask-service|
|詳細錯誤 log| kubectl describe pod <flask-app-pod-name>|
|詳細錯誤 log| kubectl logs <flask-app-pod-name>|
|修改service| kubectl edit service flask-service|


### summary
|***Command***|***Function***|
|-------------|--------------|
|kubectl get pods|List all Pods|
|kubectl get deployments|List all Deployments|
|kubectl get services|List all Services|
|kubectl get nodes|List all Kubenetes node|
|kubectl get namepspace | List all Namespaces| 


### DOCKER cmd

### 1.Difference Between docker run and docker start
|**Command**| **Description**|	**Use Case**|
|----------------|----------------|--------------|
|docker run	|Creates and starts a new container from an image. If the container doesn’t exist, it builds one.	|Used when you need a new container instance.|
docker start|	Restarts an existing, stopped container. It does not create a new one.	|Used when you want to resume a previously stopped container.|

1. docker run - Create & Start a New Container
When you use docker run, it creates a new container from an image and starts it.
``docker run -d --name my_container nginx``
	•	Creates a new container from the nginx image.
	•	Assigns the name my_container.
	•	Runs in detached mode (-d), meaning it runs in the background.

Key Characteristics of docker run

✅ Always creates a new container.<br>
✅ If the same container name already exists, it fails unless removed.<br>
✅ If you exit the container, it stays unless --rm is used.<br>


### 2.docker start - Restart an Existing Container
  If you stopped a container, docker start restarts it without creating a new one.
  ``
   docker stop my_container   # Stop the container
   docker start my_container  # Start it again
  ``
The container must already exist (from a previous docker run).
	•	Does not create a new instance.

Key Characteristics of docker start

✅ Reuses an existing container.<br>
✅ Does not create a new container.<br>
✅ Keeps existing configurations, volumes, and data.<br>




#### 3.When to Use Which?
| **Scenario** |**Command to Use**|
|--------------|----------------------|
|Run a brand new container from an image|docker run|
|Restart a stopped container|	docker start|
|Run a temporary container (auto-delete)	|docker run --rm|
|Start a container with an interactive shell	|docker run -it ubuntu /bin/bash|
|Resume a stopped container without changes|	docker start|<container_name>

Example Workflow<br>
> 1. Run a new container:<br>
  >>  ``docker run -d --name my_flask_app -p 5000:5000 flask-app``
> 2.	Stop it:
  >> ``docker stop my_flask_app``
> 3. Restart it later:
  >> ``docker start my_flask_app``

4. Bonus: Starting with attach

If you want to restart a container and attach to it:
``docker start -ai my_container``
	•	-a: Attach to the container’s output.
	•	-i: Keep input open for interaction.

Summary
|**Feature**| **docker run**|**docker start**|
|------------|-------------|---------|
|Creates a new container|	✅ Yes|	❌ No|
|Starts an existing container|	❌ No|	✅ Yes|
|Assigns a new ID	|✅ Yes|	❌ No|
|Uses an existing container	|❌ No	|✅ Yes|
|Stops when the process ends|	✅ Yes|	✅ Yes|



docker inspect 用法
docker inspect 
docker inspect -f '{{.Config.Cmd}}' 

docker exec 用法
docker exec -it <container_id> /bin/bash


docker run 
docker run -d -p 5010:5010 flask-book-app flask run --host=0.0.0.0

docker ps
如果這個命令沒有報錯，那麼 Docker 應該已經恢復正常。

docker 
docker run -d -p 5010:5010 flask-book-app

docker build -t flask-book-app .



--------------
MacOS 成功除錯誤

eval $(minikube docker-env)


確保 Docker CLI 可以正常連接
有時 DOCKER_HOST 變數會干擾 Docker 的運行，確保它沒有被設置：

unset DOCKER_HOST
然後再次嘗試：

----------------------------------

如果 macOS 上的 Docker 出現異常，無法正常運行，可以按照以下步驟進行排查與修復：

1. 確認 Docker 是否正在運行

打開 Docker Desktop（在「應用程式」中搜尋「Docker」並啟動），然後檢查 狀態欄的 Docker 圖示：

如果 Docker 沒有啟動 → 點擊 Docker 圖示，然後點擊「Start」按鈕。
如果 Docker 顯示錯誤 → 嘗試關閉並重新打開 Docker。
你也可以使用終端機命令檢查 Docker 是否正在運行：

docker info
如果顯示類似 Cannot connect to the Docker daemon，表示 Docker daemon 可能未運行。

2. 重新啟動 Docker

如果 Docker 運行異常，嘗試重新啟動它：

osascript -e 'quit app "Docker"'
open /Applications/Docker.app
或者直接在 Docker Desktop 的 GUI 界面中點擊 Restart 按鈕。

3. 確保 Docker CLI 可以正常連接

   有時 DOCKER_HOST 變數會干擾 Docker 的運行，確保它沒有被設置：

   unset DOCKER_HOST
   然後再次嘗試：

   docker ps
   如果這個命令沒有報錯，那麼 Docker 應該已經恢復正常。

4. 檢查 macOS 上的 Docker 服務狀態

   macOS 上的 Docker 不使用 systemctl 來管理，而是由 macOS 的 launchctl 控制。可以使用以下命令檢查 Docker 服務狀態：

   ps aux | grep -i docker
   如果 Docker 進程沒有運行，可以使用以下命令手動啟動它：

   open /Applications/Docker.app

5. 重置 Docker 設定

   如果 Docker 仍然無法啟動，可能需要重置 Docker 設定：

   打開 Docker Desktop。
   進入 Settings（設定） > Troubleshoot（疑難排解）。
   點擊 Reset to factory defaults（重置為出廠設置）。
   ⚠ 注意： 這會刪除所有容器、映像和 Docker 設定，請謹慎使用。


6. 檢查 Docker 安裝完整性

   如果問題仍然存在，可以嘗試重新安裝 Docker：

完全移除 Docker
rm -rf ~/Library/Application\ Support/Docker
rm -rf ~/Library/Caches/com.docker.docker
rm -rf ~/Library/Containers/com.docker.docker
rm -rf ~/Library/Preferences/com.docker.docker.plist
rm -rf ~/Library/Logs/Docker.log
下載最新版本的 Docker Desktop
前往 Docker 官方網站 下載最新版本的 Docker Desktop 並重新安裝。
7. 確保 macOS 擁有正確權限

Docker 需要一些系統權限來運行，確保 macOS 沒有阻擋它：

前往 系統設定 > 安全性與隱私 > 開發者工具，確保 Docker 被允許執行。
如果 Docker 在 M1/M2 晶片上報錯，請確保已安裝 Rosetta 2：
softwareupdate --install-rosetta
8. 檢查防火牆與網絡

有時候防火牆或網路設置會影響 Docker：

嘗試 關閉 VPN 或 關閉 macOS 防火牆
在 Docker Desktop > Settings（設定） 中 切換 network mode，或重置網路設定。
9. 重新啟動 macOS

如果以上方法都嘗試過了，還可以嘗試 重新啟動 macOS，然後打開 Docker Desktop 檢查是否恢復正常。

10. 最後的排除錯誤步驟

如果仍然無法解決，請執行以下命令來獲取詳細的 Docker 問題日誌：

docker logs <container_id>
log show --predicate 'process == "com.docker.backend"' --last 1h
這樣可以查看最近 1 小時內 Docker 的錯誤記錄，然後根據錯誤訊息進一步診斷問題。

結論
如果 docker build -t flask-book-app . 無法執行，並顯示 Cannot connect to the Docker daemon：

確保 Docker Desktop 已啟動（GUI 或 open /Applications/Docker.app）。
重新啟動 Docker（osascript -e 'quit app "Docker"' && open /Applications/Docker.app'）。
檢查 macOS 權限與網絡設置。
嘗試完全移除 Docker 並重新安裝。
按照這些步驟，應該可以讓 Docker 正常運行！🚀




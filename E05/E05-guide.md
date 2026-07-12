# Lab 05 Guide: Kubernetes

A walkthrough with hints and explanations for exercises 01–04.

---

## General Tips Across All Exercises

**kubectl command anatomy:**
```bash
kubectl <COMMAND> <RESOURCE-TYPE> <NAME> <FLAGS>
```
- `<COMMAND>` → `get`, `describe`, `apply`, `delete`, `logs`, `port-forward`, etc.
- `<RESOURCE-TYPE>` → `pods`, `deployments`, `services`, `nodes`, `namespaces`, etc.
- `-n <namespace>` / `--namespace` → target a specific namespace.
- `-A` / `--all-namespaces` → target every namespace at once. Without it, commands default to whatever namespace you're currently in (usually `default`), and it's easy to think a resource is "missing" when it's actually just sitting in `kube-system` or elsewhere.

**Golden rule for debugging:** when something doesn't behave as expected, always check these two first:
```bash
kubectl get events -A
kubectl describe <resource-type> <name>
```
`describe` gives you the full picture of a single resource (config, status, recent events); `get events` gives you the cluster's recent history, which is often where the actual error message is hiding.

**Golden rule for images in local manifests:** Kubernetes never *builds* images — a manifest only *references* an already-built image. If your image only exists in your local/minikube Docker daemon (not a registry), you must also set `imagePullPolicy: Never` on the container, or Kubernetes will try to pull it from Docker Hub and fail.

---

## Exercise 01: Install Minikube

**Goal:** Get a local single-node Kubernetes cluster running and understand the three core building blocks: Pods, Deployments, Services.

### Install & start

```bash
# Install minikube for your OS/architecture from https://minikube.sigs.k8s.io/docs/start/

minikube start          # creates and starts the local cluster
minikube status         # confirm it's running
kubectl get nodes        # should show one Ready node
```

Stopping/removing the cluster later:
```bash
minikube delete --all
```

### Key concepts

| Object | What it is |
|---|---|
| **Pod** | The smallest deployable unit — one or more tightly-coupled containers sharing network/storage. Pods are disposable; Kubernetes creates and destroys them freely. |
| **Deployment** | A controller describing *which* pod to run and *how many* replicas to keep alive. Defined in YAML, similar in spirit to a `docker-compose.yml` service. |
| **Service** | Gives a stable DNS name/IP to a changing set of pods, since individual pod IPs come and go as pods are recreated. |
| **NodePort** | A Service type that opens the *same* static port on every node in the cluster, so `<any-Node-IP>:<NodePort>` reaches the service from outside the cluster. |

### Try it hands-on

```bash
kubectl create deployment hello --image=nginx
kubectl get pods
kubectl get deployments
kubectl expose deployment hello --type=NodePort --port=80
kubectl get services
minikube service hello --url
```
The last command prints a URL you can `curl` or open in a browser to hit the nginx pod through the NodePort service.

### Troubleshooting
- **`minikube start` hangs or fails** → check your driver (Docker, VirtualBox, KVM) is installed and running.
- **`kubectl` not found** → either install it separately, or use `minikube kubectl --` as a substitute.

---

## Exercise 02: Get to Know Kubernetes

**Goal:** Get comfortable with `kubectl` as your main interface to the cluster.

### Useful commands

```bash
kubectl get <RESOURCE>              # overview of a resource type
kubectl get events                  # recent cluster history — great for troubleshooting
kubectl describe <RESOURCE> <NAME>  # in-depth detail on one resource instance
kubectl port-forward <POD|deployment>/<NAME> <HOST-PORT>:<CONTAINER-PORT>
```
`port-forward` is especially handy for debugging a pod's contents without exposing it via a Service to everyone.

### Task 1 — Check out the resources

```bash
kubectl get nodes
kubectl get namespaces
kubectl get deployments -A
kubectl get services -A
kubectl get pods -A
```
Note the `-A` flag — without it you'll only see resources in your *current* namespace, which can make the cluster look emptier than it actually is.

### Task 2 — Which namespaces have resources present?

Read the leftmost `NAMESPACE` column in the `-A` output above. On a fresh minikube cluster you'll typically see:

- **`kube-system`** → Kubernetes' own internals: `coredns` (cluster DNS), `etcd` (state store), `kube-apiserver`, `kube-scheduler`, `kube-controller-manager`, `kube-proxy`, `storage-provisioner`.
- **`kubernetes-dashboard`** → only present if you've enabled the dashboard addon.
- **`default`** → where *your own* resources land unless you specify otherwise (e.g. the `hello` deployment/service from Exercise 01).

Worth also trying:
```bash
kubectl describe node minikube
kubectl get events -A
```

---

## Exercise 03: Kubernetes Manifest

**Goal:** Translate a Docker Compose file into a Kubernetes manifest (YAML), then apply it to the cluster.

### Applying / removing a manifest

```bash
kubectl apply -f <path-to-yaml>     # create/update resources from the manifest
kubectl delete -f <path-to-yaml>    # remove them again
```

### Manifest anatomy

- One object per YAML document by default.
- Multiple objects can live in one file, separated by `---`.
- Each `kind` (Deployment, Service, etc.) has its own required fields — see the `apiVersion`/`kind`/`metadata`/`spec` structure in the example below.

### Compose → Kubernetes translation table

| Docker Compose | Kubernetes equivalent |
|---|---|
| a `services:` entry | a **Deployment** (pod template + replica count) |
| `image:` | `spec.template.spec.containers[].image` |
| `build:` | **No equivalent** — build the image separately (e.g. with `docker build`), then reference it by name with `imagePullPolicy: Never` |
| `command:` (overrides entrypoint args, e.g. MySQL's `--default-authentication-plugin=...`) | usually `args:`, **not** `command:` (which replaces the entrypoint entirely) |
| `environment:` | `env:` (list of `name`/`value` pairs) |
| `ports: "8080:80"` | split into `containerPort` (on the Deployment) **and** a Service's `port`/`targetPort`/`nodePort` |
| `depends_on:` | **No equivalent** — Kubernetes doesn't sequence startup order; pods should tolerate a dependency not being ready yet (or use an `initContainer` to wait) |
| `volumes:` | `volumeMounts` in the container + a `volumes:` block in the pod spec |
| a service name used as a hostname elsewhere (e.g. `db_container` in a connection string) | the Kubernetes **Service's `metadata.name`** must match exactly, since Services get automatic DNS entries |

> **Note:** Kubernetes resource names cannot contain underscores (`_`) — only lowercase letters, numbers, and hyphens (`-`). If your app's code hardcodes a hostname with an underscore (e.g. `db_container`), you can't name the Service that; update the hostname in the app's config to a valid name instead (e.g. `db-container` or `sql`).

### Building locally-referenced images for minikube

Since manifests can't build images, build them normally with Docker, then load them into minikube explicitly:

```bash
docker build -t db-image:latest ./L2E4
docker build -t web-image:latest ./L2E2

minikube image load db-image:latest
minikube image load web-image:latest
```
`minikube image load` works regardless of which container runtime minikube uses internally, so it's more reliable than pointing your shell at minikube's Docker daemon (`eval $(minikube docker-env)`). Confirm the images actually landed:
```bash
minikube image ls | grep -E "db-image|web-image"
```

### Example manifest (two Deployments + two Services)

`containerPort`/`targetPort` are optional — Kubernetes still routes correctly to whatever port the container listens on as long as the Service's `port` matches, so they're left out below to keep things minimal:

```bash
cat > k8s-manifest.yaml << 'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: db-deployment
spec:
  replicas: 1                      # a DB usually shouldn't be scaled naively (shared state)
  selector:
    matchLabels:
      app: db-pod
  template:
    metadata:
      labels:
        app: db-pod
    spec:
      containers:
        - name: db-container
          image: db-image:latest
          imagePullPolicy: Never
          args: ["--default-authentication-plugin=mysql_native_password"]
---
apiVersion: v1
kind: Service
metadata:
  name: db-container       # must match the app's expected hostname exactly (see note above)
spec:
  ports:
    - port: 3306
  selector:
    app: db-pod
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-deployment
spec:
  replicas: 1
  selector:
    matchLabels:
      app: web-pod
  template:
    metadata:
      labels:
        app: web-pod
    spec:
      containers:
        - name: web
          image: web-image:latest
          imagePullPolicy: Never
---
apiVersion: v1
kind: Service
metadata:
  name: web-service
spec:
  type: NodePort                   # exposes it outside the cluster, like compose's "8080:80"
  ports:
    - port: 80
      nodePort: 30080               # must be in range 30000-32767 by default
  selector:
    app: web-pod
EOF
```

### Apply and verify

```bash
kubectl apply -f k8s-manifest.yaml
kubectl get pods
kubectl get services
minikube service web-service --url
```

### Viewing logs

```bash
kubectl get pods                          # find the exact pod name first
kubectl logs <pod-name>                   # print that pod's logs
kubectl logs -f <pod-name>                # follow live, like `docker logs -f`
kubectl logs --previous <pod-name>        # logs from the pod's last crash, if it restarted
kubectl logs deployment/web-deployment    # logs from a pod belonging to that deployment
kubectl logs -l app=web-pod               # logs from all pods matching a label
```
If a pod has more than one container, add `-c <container-name>` to pick which one.

### Shelling into a pod

```bash
kubectl exec -it deployment/web-deployment -- bash
```
This drops you into an interactive shell inside a pod belonging to that deployment — same idea as `docker exec -it <name> bash`. Exit with `exit`. If the base image doesn't include `bash`, try `sh` instead.

### Debugging a broken connection between two pods

1. **Check the Service actually finds pods:**
   ```bash
   kubectl get endpoints <service-name>
   ```
   An empty result means the Service's `selector` doesn't match any pod's `labels` — compare them with `kubectl get pods --show-labels`.
2. **Test the connection from inside the calling pod:**
   ```bash
   kubectl exec -it deployment/web-deployment -- curl -s localhost/select.php
   ```
   A `200 OK` in `kubectl logs` doesn't guarantee success — app-level errors (e.g. a failed DB connection) can still return HTTP 200 with an error message in the body, so check the actual page content, not just the status code.
3. **Read the actual error text** in that output — a DNS-style error (`getaddrinfo failed`) points to a hostname/Service-name mismatch; an "Access denied" error points to DB user permissions instead.

### Common pitfalls
- **DNS resolution failure connecting to the DB** → the Service name doesn't match the hostname hardcoded in the app's code (e.g. `config.php`'s `$servername`). Fix by renaming the Service, not the app code — unless the hostname contains an underscore, in which case the app's config needs to change instead (see the naming note above).
- **`ImagePullBackOff` / `ErrImageNeverPull`** → the image isn't visible to minikube's node. Rebuild and load it explicitly: `docker build -t <image> <path>` then `minikube image load <image>`. Delete the affected pod(s) afterward so the Deployment recreates them and retries.
- **`CrashLoopBackOff` on web pod** → check `kubectl logs <pod-name>`; often the DB isn't reachable yet or has a naming mismatch.
- **NodePort out of range** → must be 30000–32767 unless the cluster's port range has been reconfigured.

---

## Exercise 04: What Am I Doing? (Discussion)

**Goal:** Understand the underlying architecture and trade-offs of Kubernetes, not just the commands.

### 1. Control plane

The "brain" of the cluster. Makes global decisions and maintains desired state, but doesn't run your application containers itself.

- **API server** — front door; every `kubectl` command talks to this.
- **etcd** — distributed key-value store holding all cluster state; the source of truth.
- **Scheduler** — decides which node a new pod runs on.
- **Controller manager** — runs control loops that compare desired vs. actual state and corrects drift (this is what recreates a pod if it dies).

On minikube, all of this typically runs on the single node itself, alongside worker duties.

### 2. Worker (node)

A machine that actually **runs** the workloads (pods/containers). Executes instructions from the control plane and reports status back.

- **kubelet** — the on-node agent that ensures the containers described in a pod spec are running and healthy.
- **Container runtime** — the software that actually runs containers (e.g. containerd).
- **kube-proxy** — implements the networking rules that let Services route traffic to the right pods (this is what makes NodePort work).

### 3. Benefits of Kubernetes
- Self-healing (crashed pods get recreated automatically)
- Declarative configuration (describe *what*, not *how*)
- Easy horizontal scaling (`replicas:` count)
- Built-in service discovery & load balancing via stable DNS names
- Portability across clusters/providers
- Rolling updates & rollbacks with no downtime

### 4. Disadvantages of Kubernetes
- Steep learning curve / high operational complexity
- Overhead not worth it for small apps (a two-container app may run simpler under plain `docker compose`)
- Control plane components themselves consume real resources
- Debugging spans multiple layers (pod → deployment → service → node → network)
- Stateful workloads (e.g. databases) are harder to manage safely at scale
- Wider ecosystem (Helm, operators, service meshes, CNI/CSI plugins) can add its own complexity and lock-in

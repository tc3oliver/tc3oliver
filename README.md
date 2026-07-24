<!-- Header -->

<p align="center">
  <img
    src="https://capsule-render.vercel.app/api?type=waving&color=0:0f172a,100:1e40af&height=165&section=header&text=Oliver%20Yu&fontSize=40&fontColor=ffffff&fontAlignY=36"
    alt="Oliver Yu"
  />
</p>

<h3 align="center">
  AI Systems Engineer · Agent Platform Architect
</h3>

<p align="center">
  Agent Runtime · Enterprise RAG · Model Serving · AI-Driven Engineering
</p>

<p align="center">
  Building production-oriented AI systems across models, knowledge, tools, infrastructure, and software delivery.
</p>

<p align="center">
  <a href="https://study.meowcoder.com">
    <img
      src="https://img.shields.io/badge/Technical%20Notes-study.meowcoder.com-1e40af?style=flat-square&logo=readthedocs&logoColor=white"
      alt="Technical Notes"
    />
  </a>
  <a href="mailto:tc3oliver@gmail.com">
    <img
      src="https://img.shields.io/badge/Email-tc3oliver%40gmail.com-334155?style=flat-square&logo=gmail&logoColor=white"
      alt="Email"
    />
  </a>
  <img
    src="https://img.shields.io/badge/Based%20in-Taiwan-475569?style=flat-square"
    alt="Based in Taiwan"
  />
</p>

---

## About

I am a Senior AI Engineer and System Architect based in Taiwan.

I design and build AI platforms that connect language models, enterprise knowledge, engineering tools, inference infrastructure, and software development workflows.

My work focuses on turning AI prototypes into systems that are deployable, measurable, permission-aware, and maintainable.

My engineering background spans system architecture, backend services, web and mobile applications, cloud infrastructure, DevOps, information security, and machine learning system integration.

---

## AI Engineering Focus

### Agent Platforms

* Stateful agent workflows and multi-agent orchestration
* Tool calling, MCP, structured output, and permission control
* Execution tracing, checkpoints, retries, and failure recovery

### Enterprise Knowledge

* RAG, hybrid retrieval, reranking, and knowledge graphs
* Code, specification, and cross-repository knowledge integration
* Citation grounding, source validation, and retrieval evaluation

### Model Infrastructure

* vLLM, ROCm, and OpenAI-compatible model gateways
* Model routing, quantization, KV cache, and memory optimization
* Latency, throughput, concurrency, and capacity analysis

### AI-Driven Engineering

* AI code review, agentic coding, and CI/CD integration
* Agent evaluation, regression testing, and observability
* Runtime security, audit trails, and policy-controlled tool execution

---

## AI Platform Architecture

```text
Applications and Engineering Workflows
                  │
                  ▼
        Agent Runtime Platform
                  │
       ┌──────────┼───────────┐
       ▼          ▼           ▼
  Knowledge     Tools      Evaluation
  Retrieval     and MCP    and Tracing
       │          │           │
       └──────────┼───────────┘
                  ▼
       Model Gateway and Router
                  │
       ┌──────────┴───────────┐
       ▼                      ▼
 Local Inference        Hosted Models
 vLLM / ROCm            API Providers
```

The platform boundary keeps models, retrieval systems, tools, policies, and evaluation components independently replaceable.

---

## Core Technologies

<p>
  <img src="https://img.shields.io/badge/Python-334155?style=flat-square&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/TypeScript-334155?style=flat-square&logo=typescript&logoColor=white" alt="TypeScript"/>
  <img src="https://img.shields.io/badge/FastAPI-334155?style=flat-square&logo=fastapi&logoColor=white" alt="FastAPI"/>
  <img src="https://img.shields.io/badge/LangGraph-334155?style=flat-square" alt="LangGraph"/>
  <img src="https://img.shields.io/badge/LangChain-334155?style=flat-square" alt="LangChain"/>
  <img src="https://img.shields.io/badge/MCP-334155?style=flat-square" alt="Model Context Protocol"/>
  <img src="https://img.shields.io/badge/RAG-334155?style=flat-square" alt="RAG"/>
  <img src="https://img.shields.io/badge/GraphRAG-334155?style=flat-square" alt="GraphRAG"/>
  <img src="https://img.shields.io/badge/vLLM-334155?style=flat-square" alt="vLLM"/>
  <img src="https://img.shields.io/badge/ROCm-334155?style=flat-square&logo=amd&logoColor=white" alt="ROCm"/>
  <img src="https://img.shields.io/badge/Docker-334155?style=flat-square&logo=docker&logoColor=white" alt="Docker"/>
  <img src="https://img.shields.io/badge/GitLab%20CI-334155?style=flat-square&logo=gitlab&logoColor=white" alt="GitLab CI"/>
  <img src="https://img.shields.io/badge/Jenkins-334155?style=flat-square&logo=jenkins&logoColor=white" alt="Jenkins"/>
  <img src="https://img.shields.io/badge/PostgreSQL-334155?style=flat-square&logo=postgresql&logoColor=white" alt="PostgreSQL"/>
  <img src="https://img.shields.io/badge/Redis-334155?style=flat-square&logo=redis&logoColor=white" alt="Redis"/>
  <img src="https://img.shields.io/badge/Qdrant-334155?style=flat-square" alt="Qdrant"/>
  <img src="https://img.shields.io/badge/Neo4j-334155?style=flat-square&logo=neo4j&logoColor=white" alt="Neo4j"/>
</p>

<details>
  <summary><strong>Additional Engineering Experience</strong></summary>
  <br/>

* **Architecture:** REST, gRPC, API gateways, authentication, RBAC, and asynchronous services
* **Infrastructure:** Docker, AWS ECS, Terraform, monitoring, and automated deployment
* **Data:** PostgreSQL, SQL Server, Redis, vector databases, and graph databases
* **Applications:** Vue, React, PWA, Flutter, native iOS, and native Android
* **Engineering:** Static analysis, testing, observability, security controls, and release governance

</details>

---

## Technical Writing

I publish research notes and technical analysis on:

* AI agent architecture and runtime engineering
* Enterprise RAG and knowledge systems
* Model inference and serving optimization
* Agent security and runtime governance
* AI-assisted software development
* Software architecture and engineering automation

<p>
  <a href="https://study.meowcoder.com">
    <img
      src="https://img.shields.io/badge/Read%20Technical%20Notes-MeowCoder%20Lab-1e40af?style=flat-square&logo=markdown&logoColor=white"
      alt="MeowCoder Lab"
    />
  </a>
</p>

---

## GitHub Activity

<p align="center">
  <img
    src="./github-metrics.svg"
    width="100%"
    alt="Oliver Yu GitHub Metrics"
  />
</p>

---

## Engineering Principles

> Models are replaceable. Runtime boundaries and evaluation loops are architecture.

AI systems should remain:

* **Traceable** — decisions, sources, and execution paths can be inspected
* **Testable** — retrieval, routing, tools, and outputs can be regression-tested
* **Replaceable** — models and providers remain interchangeable
* **Permission-aware** — tool access follows explicit runtime policies
* **Observable** — quality, latency, cost, usage, and failures remain measurable
* **Recoverable** — workflows support retries, checkpoints, and controlled failure

<p align="center">
  <img
    src="https://capsule-render.vercel.app/api?type=waving&color=0:1e40af,100:0f172a&height=90&section=footer"
    alt="Footer"
  />
</p>

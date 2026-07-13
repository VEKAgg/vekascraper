# On-disk layout

```
/data/
├── jobs/
│   ├── JOB-20260713-a3f8k.json
│   └── JOB-20260713-b7x2p.json
├── logs/
│   ├── JOB-20260713-a3f8k.log
│   └── JOB-20260713-b7x2p.log
├── manifests/
│   ├── JOB-20260713-a3f8k.json
│   └── JOB-20260713-b7x2p.json
├── exports/
│   ├── messages/
│   │   └── JOB-20260713-b7x2p/
│   │       ├── channel-123456/
│   │       │   ├── messages.csv
│   │       │   └── messages.json
│   │       └── channel-789012/
│   │           ├── messages.csv
│   │           └── messages.json
│   └── members/
│       └── JOB-20260713-a3f8k/
│           ├── members.json
│           └── roles.json
└── temp/
    └── .gitkeep
```

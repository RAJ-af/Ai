# AI Developer Team

This project implements an autonomous AI developer team capable of interviewing a user, creating a PRD/Plan, and generating source code for a project.

## Features
- **Boss AI**: Interviews the user to gather requirements.
- **Planner AI**: Creates a detailed Markdown PRD and technical plan.
- **CEO AI**: Manages specialized agents (UI/UX, Frontend, Backend, QA, DevOps).
- **Automated Zipping**: Collects all generated code blocks and packages them into a ZIP file.
- **NVIDIA NIM Integration**: Uses high-performance NVIDIA models.

## Deployment on Hugging Face
1. Create a new Space on Hugging Face (Gradio SDK).
2. Upload all files.
3. Add your `NVIDIA_API_KEY` to the Space's Secrets.
4. Enjoy!

## Tech Stack
- LangChain
- Gradio
- NVIDIA NIM (NVIDIA AI Endpoints)

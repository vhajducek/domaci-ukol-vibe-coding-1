# Penalty Interest Calculator (LLM + Tool Calling)

This project demonstrates how a Large Language Model (LLM) can call a Python function (tool) to calculate penalty interest.

## Features
- Uses Ollama (llama3.2)
- Function calling (tool usage)
- Calculates penalty interest for overdue payments
- Returns final human-readable answer

## Example
Input:
Calculate penalty interest on a 150000 CZK debt with 12% annual rate that is 45 days overdue.

Output:
The penalty interest is 2,219.18 CZK, so the total amount due is 152,219.18 CZK.

## How it works
1. LLM receives user question
2. Calls Python tool `penalty_interest`
3. Python calculates result
4. Result is sent back to LLM
5. LLM produces final answer

## Run
Make sure Ollama is running:

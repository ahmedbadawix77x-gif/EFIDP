<#
.SYNOPSIS
    EFIDP Platform Developer Task Runner for Windows PowerShell.
.DESCRIPTION
    Provides shortcuts for linting, formatting, type checking, testing, and environment setup.
.EXAMPLE
    .\scripts\dev.ps1 lint
    .\scripts\dev.ps1 test
    .\scripts\dev.ps1 check
#>

param (
    [Parameter(Position=0)]
    [ValidateSet("install", "lint", "format", "format-fix", "typecheck", "test", "test-cov", "check", "clean")]
    [string]$Task = "check"
)

$ErrorActionPreference = "Stop"

switch ($Task) {
    "install" {
        Write-Host "Installing dependencies in editable mode..." -ForegroundColor Cyan
        & .venv\Scripts\python.exe -m pip install --upgrade pip
        & .venv\Scripts\python.exe -m pip install -e ".[dev]"
    }
    "lint" {
        Write-Host "Running Ruff linter..." -ForegroundColor Cyan
        & .venv\Scripts\ruff.exe check .
    }
    "format" {
        Write-Host "Checking Ruff code formatting..." -ForegroundColor Cyan
        & .venv\Scripts\ruff.exe format --check .
    }
    "format-fix" {
        Write-Host "Applying Ruff format and lint fixes..." -ForegroundColor Cyan
        & .venv\Scripts\ruff.exe format .
        & .venv\Scripts\ruff.exe check --fix .
    }
    "typecheck" {
        Write-Host "Running MyPy static type checking..." -ForegroundColor Cyan
        & .venv\Scripts\mypy.exe src tests
    }
    "test" {
        Write-Host "Running Pytest suite..." -ForegroundColor Cyan
        & .venv\Scripts\pytest.exe tests
    }
    "test-cov" {
        Write-Host "Running Pytest with coverage verification..." -ForegroundColor Cyan
        & .venv\Scripts\pytest.exe --cov=src/efidp --cov-report=term-missing --cov-report=html
    }
    "check" {
        Write-Host "Executing full quality gate..." -ForegroundColor Green
        & .venv\Scripts\ruff.exe check .
        & .venv\Scripts\ruff.exe format --check .
        & .venv\Scripts\mypy.exe src tests
        & .venv\Scripts\pytest.exe --cov=src/efidp --cov-report=term-missing
    }
    "clean" {
        Write-Host "Cleaning temporary artifacts..." -ForegroundColor Yellow
        Get-ChildItem -Path . -Include __pycache__, .pytest_cache, .mypy_cache, .ruff_cache, htmlcov -Recurse -Force -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force
        Remove-Item -Path .coverage -Force -ErrorAction SilentlyContinue
    }
}

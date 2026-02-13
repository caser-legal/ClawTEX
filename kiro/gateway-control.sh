#!/bin/bash
# CLAWTEX Gateway Control

PID_FILE="$HOME/.kiro/gateway.pid"
LOG_FILE="$HOME/.kiro/logs/gateway.log"
GATEWAY_SCRIPT="$HOME/.kiro/gateway.py"

case "$1" in
    start)
        if [ -f "$PID_FILE" ]; then
            PID=$(cat "$PID_FILE")
            if ps -p "$PID" > /dev/null 2>&1; then
                echo "✅ Gateway already running (PID: $PID)"
                exit 0
            fi
        fi
        
        echo "🚀 Starting CLAWTEX gateway..."
        nohup python3 "$GATEWAY_SCRIPT" > /dev/null 2>&1 &
        sleep 2
        
        if [ -f "$PID_FILE" ]; then
            PID=$(cat "$PID_FILE")
            echo "✅ Gateway started (PID: $PID)"
            echo "   Heartbeat: Every 15 minutes"
            echo "   Logs: tail -f $LOG_FILE"
        else
            echo "❌ Failed to start gateway"
            exit 1
        fi
        ;;
        
    stop)
        if [ ! -f "$PID_FILE" ]; then
            echo "❌ Gateway not running"
            exit 1
        fi
        
        PID=$(cat "$PID_FILE")
        echo "🛑 Stopping gateway (PID: $PID)..."
        kill "$PID" 2>/dev/null
        sleep 1
        
        if ps -p "$PID" > /dev/null 2>&1; then
            echo "⚠️  Force killing..."
            kill -9 "$PID" 2>/dev/null
        fi
        
        rm -f "$PID_FILE"
        echo "✅ Gateway stopped"
        ;;
        
    status)
        if [ -f "$PID_FILE" ]; then
            PID=$(cat "$PID_FILE")
            if ps -p "$PID" > /dev/null 2>&1; then
                echo "✅ Gateway is RUNNING (PID: $PID)"
                echo "   Heartbeat: Every 15 minutes"
                echo "   Logs: $LOG_FILE"
            else
                echo "❌ Gateway PID file exists but process is dead"
                rm -f "$PID_FILE"
            fi
        else
            echo "❌ Gateway is NOT RUNNING"
            echo "   Start with: clawtex-gateway start"
        fi
        ;;
        
    logs)
        tail -f "$LOG_FILE"
        ;;
        
    restart)
        $0 stop
        sleep 2
        $0 start
        ;;
        
    *)
        echo "CLAWTEX Gateway Control"
        echo ""
        echo "Usage: clawtex-gateway {start|stop|restart|status|logs}"
        echo ""
        echo "Commands:"
        echo "  start    - Start gateway with 15-min heartbeat"
        echo "  stop     - Stop gateway"
        echo "  restart  - Restart gateway"
        echo "  status   - Check if running"
        echo "  logs     - Watch gateway logs"
        ;;
esac

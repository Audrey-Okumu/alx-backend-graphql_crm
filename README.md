# CRM Celery Setup Guide

## Setup Steps

1. **Install Dependencies**
```
   pip install -r requirements.txt
   sudo apt install redis-server
```
2. **Run Migrations**
```
python manage.py migrate
```

3.**Start Redis**
```
sudo service redis-server start
```

4. **Start Celery Worker**
```
celery -A crm worker -l info
```


5. **Start Celery Beat**
```
celery -A crm beat -l info
```


6. **Verify Logs**
Check /tmp/crm_report_log.txt for generated weekly reports.

---

##  Summary of Created/Modified Files
| File | Purpose |
|------|----------|
| `requirements.txt` | Added Celery & django-celery-beat |
| `crm/settings.py` | Added Celery config + Beat schedule |
| `crm/celery.py` | Celery initialization |
| `crm/__init__.py` | Auto-load Celery |
| `crm/tasks.py` | Report generation task |
| `crm/README.md` | Setup instructions |

---


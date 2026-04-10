@echo off
setlocal

echo Running regression test suite...
echo.

echo ==> Unit tests (service)
python manage.py test products.tests_service_unit
if errorlevel 1 (
  echo Step failed: Unit tests (service)
  exit /b %errorlevel%
)

echo.
echo ==> Integration API tests
python manage.py test products.tests_integration_api
if errorlevel 1 (
  echo Step failed: Integration API tests
  exit /b %errorlevel%
)

echo.
echo ==> Full products test suite
python manage.py test products
if errorlevel 1 (
  echo Step failed: Full products test suite
  exit /b %errorlevel%
)

echo.
echo Regression suite completed successfully.
exit /b 0

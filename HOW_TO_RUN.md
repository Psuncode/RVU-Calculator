# How to Run the RVU Calculator

## Quick Start (Easiest Method)

1. **Double-click** the file: `START_RVU_CALCULATOR.command`
2. Your browser will open automatically
3. The calculator is ready to use!

To stop the server:
- Return to the terminal window
- Press `Ctrl+C`

---

## What This Does

The launcher script:
- Starts a local web server on port 8000
- Opens your default browser to http://localhost:8000
- Allows the calculator to load data files correctly

---

## Alternative Manual Method

If you prefer to start the server manually:

### Using Python (recommended)
```bash
cd "/Users/philipsun/Downloads/Validation/Granger work Folder/RVU Look up/RVU Calculator/app"
python3 -m http.server 8000
```
Then open: http://localhost:8000

### Using PHP
```bash
cd "/Users/philipsun/Downloads/Validation/Granger work Folder/RVU Look up/RVU Calculator/app"
php -S localhost:8000
```
Then open: http://localhost:8000

### Using Node.js
```bash
cd "/Users/philipsun/Downloads/Validation/Granger work Folder/RVU Look up/RVU Calculator/app"
npx http-server -p 8000
```
Then open: http://localhost:8000

---

## Troubleshooting

### "Port 8000 is already in use"
Another program is using port 8000. Either:
- Stop that program
- Or change the port in the script (e.g., 8001, 8080, 3000)

### "No web server available"
Install Python 3, Node.js, or ensure PHP is available:
- Python 3: https://www.python.org/downloads/
- Node.js: https://nodejs.org/

### Data doesn't load
Make sure you're accessing via http://localhost:8000, NOT by opening index.html directly.

---

## Technical Details

**Why is a server needed?**
Modern browsers block loading local files via JavaScript fetch() when opening HTML files directly (file:// protocol) due to CORS security policy. Running a local server (http://) allows the browser to load the data files.

**Is this secure?**
Yes! The server only runs on your computer (localhost) and is not accessible from the internet.

**Can I share this?**
Yes! Just share the entire RVU Calculator folder with the START_RVU_CALCULATOR.command file.

---

## Features

The RVU Calculator includes:
- **Simplified GPCI Display**: Locality dropdown shows clean names (e.g., "UTAH")
- **Multi-Year Comparison Table**: View 2019-2025 RVU data side-by-side
- **Dynamic Updates**: Change year, locality, POS, or CF to see instant recalculations
- **Year-over-Year Analysis**: Green/red indicators show RVU trends
- **Responsive Design**: Works on desktop, tablet, and mobile browsers

---

## Quick Test

After starting the server:
1. Enter CPT code: **99213**
2. Click "Multi-Year Comparison (2019-2025)" to expand
3. Enter Conversion Factor: **33.89**
4. You should see 7 years of data with payment calculations

Enjoy using the RVU Calculator!

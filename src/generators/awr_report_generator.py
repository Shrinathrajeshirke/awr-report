import random
import datetime
import os
from pathlib import Path

class AWRReportGenerator:
    """Generate realistic Oracle AWR reports with various anomaly patterns"""
    
    def __init__(self):
        self.db_names = ['PROD_CRM', 'PROD_ERP', 'PROD_WEB', 'PROD_ANALYTICS', 'PROD_HR']
        self.anomaly_types = ['NORMAL', 'CPU_SPIKE', 'MEMORY_PRESSURE', 'IO_BOTTLENECK', 
                             'LOCK_CONTENTION', 'TEMP_SPACE', 'NETWORK_LATENCY']
        
        # SQL templates for variety
        self.sql_templates = [
            "SELECT * FROM orders WHERE order_date > :1",
            "UPDATE customer SET last_login = SYSDATE WHERE id = :1",
            "INSERT INTO audit_log VALUES (:1, :2, :3)",
            "SELECT COUNT(*) FROM products WHERE category = :1",
            "DELETE FROM temp_data WHERE session_id = :1",
            "SELECT o.*, c.name FROM orders o JOIN customers c ON o.cust_id = c.id",
            "UPDATE inventory SET quantity = quantity - :1 WHERE product_id = :2",
            "SELECT * FROM users WHERE last_login < SYSDATE - 30",
            "INSERT INTO transactions (id, amount, date) VALUES (:1, :2, :3)",
            "SELECT AVG(price) FROM products GROUP BY category"
        ]
    
    def generate_reports(self, count=300, output_dir='data/raw_awr_reports'):
        """Generate multiple AWR reports with specified distribution"""
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Distribution: 80% normal, 20% anomalies
        normal_count = int(count * 0.80)
        anomaly_count = count - normal_count
        
        report_types = ['NORMAL'] * normal_count
        
        # Distribute anomalies across types
        for i in range(anomaly_count):
            anomaly_type = random.choice(self.anomaly_types[1:])  # Exclude NORMAL
            report_types.append(anomaly_type)
        
        random.shuffle(report_types)
        
        print(f"Generating {count} AWR reports...")
        print(f"  - Normal: {normal_count}")
        print(f"  - Anomalies: {anomaly_count}")
        
        for i, report_type in enumerate(report_types, 1):
            filename = f"{output_dir}/AWR_{report_type}_{i:04d}.html"
            self._generate_single_report(filename, report_type, i)
            
            if i % 50 == 0:
                print(f"  Generated {i}/{count} reports...")
        
        print(f"✓ All {count} reports generated in '{output_dir}'")
        return output_dir
    
    def _generate_single_report(self, filename, anomaly_type, report_num):
        """Generate a single AWR report"""
        
        # Random timestamp (last 90 days)
        days_ago = random.randint(0, 90)
        end_time = datetime.datetime.now() - datetime.timedelta(days=days_ago)
        start_time = end_time - datetime.timedelta(hours=1)
        
        # Database identification
        db_name = random.choice(self.db_names) + f"_{random.randint(100, 999)}"
        db_id = random.randint(1000000000, 9999999999)
        instance = random.randint(1, 4)
        
        # Generate metrics based on anomaly type
        metrics = self._generate_metrics(anomaly_type)
        
        # Generate HTML report
        html = self._build_html(db_name, db_id, instance, start_time, end_time, 
                               metrics, anomaly_type, report_num)
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html)
    
    def _generate_metrics(self, anomaly_type):
        """Generate metrics based on anomaly type"""
        
        if anomaly_type == 'NORMAL':
            return {
                'db_time_per_sec': round(random.uniform(0.3, 0.8), 2),
                'db_cpu_per_sec': round(random.uniform(0.2, 0.5), 2),
                'redo_size': random.randint(80000, 150000),
                'logical_reads': random.randint(800, 1500),
                'physical_reads': random.randint(50, 200),
                'executes': random.randint(100, 200),
                'transactions': round(random.uniform(2.5, 4.5), 2),
                'buffer_hit': round(random.uniform(95, 99), 2),
                'library_hit': round(random.uniform(97, 99.5), 2),
                'soft_parse': round(random.uniform(94, 98), 2),
                'latch_hit': round(random.uniform(99, 99.9), 2),
                'cpu_time': round(random.uniform(800, 1800), 2),
                'cpu_pct_db': round(random.uniform(40, 70), 1),
                'seq_read_waits': random.randint(20000, 50000),
                'seq_read_time': round(random.uniform(20, 60), 2),
                'seq_read_avg': round(random.uniform(0.3, 0.8), 2),
                'log_sync_waits': random.randint(8000, 15000),
                'log_sync_time': round(random.uniform(5, 15), 2),
                'sga_size': random.choice([2048, 4096, 8192]),
                'pga_allocated': random.randint(512, 1024),
                'pga_used': random.randint(300, 700),
                'os_cpu_usage': round(random.uniform(30, 60), 1),
                'load_average': round(random.uniform(1.5, 3.5), 1),
                'parse_time_pct': round(random.uniform(5, 15), 1),
                'hard_parse_pct': round(random.uniform(2, 6), 1),
                'sorts_memory': random.randint(8000, 15000),
                'sorts_disk': random.randint(0, 50)
            }
        
        elif anomaly_type == 'CPU_SPIKE':
            return {
                'db_time_per_sec': round(random.uniform(1.5, 3.0), 2),
                'db_cpu_per_sec': round(random.uniform(1.0, 2.5), 2),
                'redo_size': random.randint(150000, 300000),
                'logical_reads': random.randint(2000, 4000),
                'physical_reads': random.randint(100, 300),
                'executes': random.randint(250, 400),
                'transactions': round(random.uniform(5.0, 8.0), 2),
                'buffer_hit': round(random.uniform(93, 97), 2),
                'library_hit': round(random.uniform(95, 98), 2),
                'soft_parse': round(random.uniform(85, 92), 2),
                'latch_hit': round(random.uniform(98, 99.5), 2),
                'cpu_time': round(random.uniform(3500, 7000), 2),
                'cpu_pct_db': round(random.uniform(75, 90), 1),
                'seq_read_waits': random.randint(30000, 60000),
                'seq_read_time': round(random.uniform(40, 100), 2),
                'seq_read_avg': round(random.uniform(0.5, 1.2), 2),
                'log_sync_waits': random.randint(15000, 25000),
                'log_sync_time': round(random.uniform(15, 35), 2),
                'sga_size': random.choice([2048, 4096, 8192]),
                'pga_allocated': random.randint(1024, 2048),
                'pga_used': random.randint(800, 1800),
                'os_cpu_usage': round(random.uniform(85, 98), 1),
                'load_average': round(random.uniform(6.5, 12.0), 1),
                'parse_time_pct': round(random.uniform(20, 35), 1),
                'hard_parse_pct': round(random.uniform(10, 20), 1),
                'sorts_memory': random.randint(15000, 30000),
                'sorts_disk': random.randint(50, 200)
            }
        
        elif anomaly_type == 'MEMORY_PRESSURE':
            return {
                'db_time_per_sec': round(random.uniform(1.0, 2.0), 2),
                'db_cpu_per_sec': round(random.uniform(0.3, 0.7), 2),
                'redo_size': random.randint(100000, 200000),
                'logical_reads': random.randint(1500, 3000),
                'physical_reads': random.randint(800, 2000),
                'executes': random.randint(150, 300),
                'transactions': round(random.uniform(3.0, 6.0), 2),
                'buffer_hit': round(random.uniform(75, 88), 2),
                'library_hit': round(random.uniform(85, 93), 2),
                'soft_parse': round(random.uniform(80, 90), 2),
                'latch_hit': round(random.uniform(97, 99), 2),
                'cpu_time': round(random.uniform(1000, 2500), 2),
                'cpu_pct_db': round(random.uniform(30, 50), 1),
                'seq_read_waits': random.randint(80000, 150000),
                'seq_read_time': round(random.uniform(200, 500), 2),
                'seq_read_avg': round(random.uniform(1.5, 3.5), 2),
                'log_sync_waits': random.randint(10000, 20000),
                'log_sync_time': round(random.uniform(10, 25), 2),
                'sga_size': random.choice([2048, 4096, 8192]),
                'pga_allocated': random.randint(1536, 3072),
                'pga_used': random.randint(1400, 2900),
                'os_cpu_usage': round(random.uniform(45, 70), 1),
                'load_average': round(random.uniform(3.5, 6.5), 1),
                'parse_time_pct': round(random.uniform(8, 18), 1),
                'hard_parse_pct': round(random.uniform(15, 30), 1),
                'sorts_memory': random.randint(3000, 8000),
                'sorts_disk': random.randint(500, 2000)
            }
        
        elif anomaly_type == 'IO_BOTTLENECK':
            return {
                'db_time_per_sec': round(random.uniform(1.2, 2.5), 2),
                'db_cpu_per_sec': round(random.uniform(0.2, 0.5), 2),
                'redo_size': random.randint(200000, 400000),
                'logical_reads': random.randint(2000, 4000),
                'physical_reads': random.randint(1000, 3000),
                'executes': random.randint(100, 250),
                'transactions': round(random.uniform(2.0, 5.0), 2),
                'buffer_hit': round(random.uniform(80, 90), 2),
                'library_hit': round(random.uniform(93, 97), 2),
                'soft_parse': round(random.uniform(90, 96), 2),
                'latch_hit': round(random.uniform(98, 99.5), 2),
                'cpu_time': round(random.uniform(600, 1500), 2),
                'cpu_pct_db': round(random.uniform(15, 35), 1),
                'seq_read_waits': random.randint(120000, 250000),
                'seq_read_time': round(random.uniform(400, 900), 2),
                'seq_read_avg': round(random.uniform(2.0, 5.0), 2),
                'log_sync_waits': random.randint(8000, 18000),
                'log_sync_time': round(random.uniform(80, 180), 2),
                'sga_size': random.choice([2048, 4096, 8192]),
                'pga_allocated': random.randint(512, 1024),
                'pga_used': random.randint(400, 900),
                'os_cpu_usage': round(random.uniform(35, 55), 1),
                'load_average': round(random.uniform(2.5, 5.5), 1),
                'parse_time_pct': round(random.uniform(5, 12), 1),
                'hard_parse_pct': round(random.uniform(3, 8), 1),
                'sorts_memory': random.randint(9000, 14000),
                'sorts_disk': random.randint(100, 400)
            }
        
        elif anomaly_type == 'LOCK_CONTENTION':
            return {
                'db_time_per_sec': round(random.uniform(1.3, 2.2), 2),
                'db_cpu_per_sec': round(random.uniform(0.3, 0.6), 2),
                'redo_size': random.randint(90000, 180000),
                'logical_reads': random.randint(1000, 2000),
                'physical_reads': random.randint(80, 250),
                'executes': random.randint(120, 250),
                'transactions': round(random.uniform(2.0, 4.5), 2),
                'buffer_hit': round(random.uniform(94, 98), 2),
                'library_hit': round(random.uniform(96, 99), 2),
                'soft_parse': round(random.uniform(92, 97), 2),
                'latch_hit': round(random.uniform(92, 96), 2),
                'cpu_time': round(random.uniform(900, 2000), 2),
                'cpu_pct_db': round(random.uniform(25, 45), 1),
                'seq_read_waits': random.randint(25000, 55000),
                'seq_read_time': round(random.uniform(30, 80), 2),
                'seq_read_avg': round(random.uniform(0.6, 1.5), 2),
                'log_sync_waits': random.randint(10000, 20000),
                'log_sync_time': round(random.uniform(50, 120), 2),
                'sga_size': random.choice([2048, 4096, 8192]),
                'pga_allocated': random.randint(512, 1024),
                'pga_used': random.randint(350, 850),
                'os_cpu_usage': round(random.uniform(40, 65), 1),
                'load_average': round(random.uniform(2.8, 5.2), 1),
                'parse_time_pct': round(random.uniform(6, 14), 1),
                'hard_parse_pct': round(random.uniform(4, 9), 1),
                'sorts_memory': random.randint(8500, 14500),
                'sorts_disk': random.randint(20, 100),
                'enqueue_waits': random.randint(5000, 15000),
                'enqueue_time': round(random.uniform(300, 800), 2)
            }
        
        elif anomaly_type == 'TEMP_SPACE':
            return {
                'db_time_per_sec': round(random.uniform(1.1, 2.0), 2),
                'db_cpu_per_sec': round(random.uniform(0.4, 0.8), 2),
                'redo_size': random.randint(110000, 220000),
                'logical_reads': random.randint(1800, 3500),
                'physical_reads': random.randint(300, 800),
                'executes': random.randint(130, 280),
                'transactions': round(random.uniform(2.8, 5.5), 2),
                'buffer_hit': round(random.uniform(90, 95), 2),
                'library_hit': round(random.uniform(94, 98), 2),
                'soft_parse': round(random.uniform(88, 94), 2),
                'latch_hit': round(random.uniform(98, 99.5), 2),
                'cpu_time': round(random.uniform(1500, 3000), 2),
                'cpu_pct_db': round(random.uniform(35, 55), 1),
                'seq_read_waits': random.randint(30000, 70000),
                'seq_read_time': round(random.uniform(50, 120), 2),
                'seq_read_avg': round(random.uniform(0.8, 2.0), 2),
                'log_sync_waits': random.randint(9000, 17000),
                'log_sync_time': round(random.uniform(8, 20), 2),
                'sga_size': random.choice([2048, 4096, 8192]),
                'pga_allocated': random.randint(1024, 2048),
                'pga_used': random.randint(900, 1900),
                'os_cpu_usage': round(random.uniform(55, 75), 1),
                'load_average': round(random.uniform(4.0, 7.5), 1),
                'parse_time_pct': round(random.uniform(10, 20), 1),
                'hard_parse_pct': round(random.uniform(8, 16), 1),
                'sorts_memory': random.randint(2000, 6000),
                'sorts_disk': random.randint(1000, 4000),
                'temp_space_used': random.randint(15000, 35000)
            }
        
        else:  # NETWORK_LATENCY
            return {
                'db_time_per_sec': round(random.uniform(0.9, 1.8), 2),
                'db_cpu_per_sec': round(random.uniform(0.2, 0.5), 2),
                'redo_size': random.randint(95000, 180000),
                'logical_reads': random.randint(1100, 2200),
                'physical_reads': random.randint(70, 220),
                'executes': random.randint(110, 230),
                'transactions': round(random.uniform(2.5, 5.0), 2),
                'buffer_hit': round(random.uniform(95, 98.5), 2),
                'library_hit': round(random.uniform(96, 99), 2),
                'soft_parse': round(random.uniform(93, 97), 2),
                'latch_hit': round(random.uniform(98.5, 99.7), 2),
                'cpu_time': round(random.uniform(700, 1600), 2),
                'cpu_pct_db': round(random.uniform(20, 40), 1),
                'seq_read_waits': random.randint(22000, 48000),
                'seq_read_time': round(random.uniform(25, 65), 2),
                'seq_read_avg': round(random.uniform(0.4, 1.0), 2),
                'log_sync_waits': random.randint(8500, 16000),
                'log_sync_time': round(random.uniform(6, 18), 2),
                'sga_size': random.choice([2048, 4096, 8192]),
                'pga_allocated': random.randint(512, 1024),
                'pga_used': random.randint(350, 800),
                'os_cpu_usage': round(random.uniform(32, 58), 1),
                'load_average': round(random.uniform(1.8, 4.2), 1),
                'parse_time_pct': round(random.uniform(5, 13), 1),
                'hard_parse_pct': round(random.uniform(3, 7), 1),
                'sorts_memory': random.randint(8200, 14800),
                'sorts_disk': random.randint(10, 80),
                'sql_net_waits': random.randint(15000, 40000),
                'sql_net_time': round(random.uniform(200, 600), 2)
            }
    
    def _build_html(self, db_name, db_id, instance, start_time, end_time, 
                    metrics, anomaly_type, report_num):
        """Build complete HTML report"""
        
        elapsed_min = 60.0
        db_time_min = round(metrics['db_time_per_sec'] * 3600 / 60, 2)
        
        # Calculate derived metrics
        db_time_per_txn = round(metrics['db_time_per_sec'] / metrics['transactions'], 2)
        db_cpu_per_txn = round(metrics['db_cpu_per_sec'] / metrics['transactions'], 2)
        redo_per_txn = int(metrics['redo_size'] / metrics['transactions'])
        logical_per_txn = int(metrics['logical_reads'] / metrics['transactions'])
        physical_per_txn = int(metrics['physical_reads'] / metrics['transactions'])
        exec_per_txn = int(metrics['executes'] / metrics['transactions'])
        
        pga_usage_pct = round((metrics['pga_used'] / metrics['pga_allocated']) * 100, 1)
        
        # Determine anomaly class for highlighting
        def get_class(metric_name):
            if anomaly_type == 'NORMAL':
                return ''
            
            anomaly_metrics = {
                'CPU_SPIKE': ['db_time_per_sec', 'cpu_time', 'cpu_pct_db', 'os_cpu_usage', 'load_average', 'hard_parse_pct'],
                'MEMORY_PRESSURE': ['buffer_hit', 'physical_reads', 'pga_usage_pct', 'sorts_disk', 'hard_parse_pct', 'seq_read_time'],
                'IO_BOTTLENECK': ['physical_reads', 'seq_read_time', 'seq_read_avg', 'buffer_hit', 'log_sync_time'],
                'LOCK_CONTENTION': ['enqueue_time', 'latch_hit', 'db_time_per_sec', 'log_sync_time'],
                'TEMP_SPACE': ['sorts_disk', 'temp_space_used', 'pga_usage_pct', 'hard_parse_pct'],
                'NETWORK_LATENCY': ['sql_net_time', 'sql_net_waits']
            }
            
            if metric_name in anomaly_metrics.get(anomaly_type, []):
                return 'anom'
            return ''
        
        # Build SQL section with random queries
        sql_rows = []
        for i in range(8):
            sql_id = ''.join(random.choices('0123456789abcdef', k=8))
            execs = random.randint(500, 5000)
            elapsed = round(random.uniform(1.0, 5.5), 2)
            cpu = round(random.uniform(0.3, 4.0), 2)
            sql_text = random.choice(self.sql_templates)
            
            sql_rows.append(f'<tr><td>{sql_id}</td><td class="r">{execs:,}</td>'
                          f'<td class="r">{elapsed}</td><td class="r">{cpu}</td>'
                          f'<td>{sql_text}</td></tr>')
        
        sql_section = '\n'.join(sql_rows)
        
        # Build wait events section
        seq_read_pct = round(metrics['seq_read_time']/db_time_min*60*100, 1) if db_time_min > 0 else 0
        log_sync_pct = round(metrics['log_sync_time']/db_time_min*60*100, 1) if db_time_min > 0 else 0
        
        wait_events_html = f'''<tr><td class="{get_class('cpu_time')}">CPU time</td>
<td class="r">0</td><td class="r">{metrics['cpu_time']}</td><td class="r">0</td>
<td class="r">{metrics['cpu_pct_db']}</td></tr>
<tr><td class="{get_class('seq_read_time')}">db file sequential read</td>
<td class="r">{metrics['seq_read_waits']:,}</td><td class="r">{metrics['seq_read_time']}</td>
<td class="r">{metrics['seq_read_avg']}</td><td class="r">{seq_read_pct}</td></tr>
<tr><td class="{get_class('log_sync_time')}">log file sync</td><td class="r">{metrics['log_sync_waits']:,}</td>
<td class="r">{metrics['log_sync_time']}</td><td class="r">{round(metrics['log_sync_time']/metrics['log_sync_waits']*1000, 2) if metrics['log_sync_waits'] > 0 else 0}</td>
<td class="r">{log_sync_pct}</td></tr>'''
        
        # Add specific anomaly wait events
        if anomaly_type == 'LOCK_CONTENTION' and 'enqueue_waits' in metrics:
            enq_pct = round(metrics['enqueue_time']/db_time_min*60*100, 1) if db_time_min > 0 else 0
            wait_events_html += f'''<tr><td class="anom">enq: TX - row lock contention</td>
<td class="r">{metrics['enqueue_waits']:,}</td><td class="r">{metrics['enqueue_time']}</td>
<td class="r">{round(metrics['enqueue_time']/metrics['enqueue_waits']*1000, 2) if metrics['enqueue_waits'] > 0 else 0}</td>
<td class="r">{enq_pct}</td></tr>'''
        
        if anomaly_type == 'NETWORK_LATENCY' and 'sql_net_waits' in metrics:
            net_pct = round(metrics['sql_net_time']/db_time_min*60*100, 1) if db_time_min > 0 else 0
            wait_events_html += f'''<tr><td class="anom">SQL*Net more data from client</td>
<td class="r">{metrics['sql_net_waits']:,}</td><td class="r">{metrics['sql_net_time']}</td>
<td class="r">{round(metrics['sql_net_time']/metrics['sql_net_waits']*1000, 2) if metrics['sql_net_waits'] > 0 else 0}</td>
<td class="r">{net_pct}</td></tr>'''
        
        # Time Model section
        time_model_html = f'''<div class="sec">
<h2>Time Model Statistics</h2>
<table>
<tr><th>Statistic</th><th class="r">Time (s)</th><th class="r">% DB Time</th></tr>
<tr><td>sql execute elapsed time</td><td class="r">{round(db_time_min*60*0.6, 1)}</td><td class="r">60.0</td></tr>
<tr><td class="{get_class('hard_parse_pct')}">parse time elapsed</td>
<td class="r">{round(db_time_min*60*metrics['parse_time_pct']/100, 1)}</td>
<td class="r">{metrics['parse_time_pct']}</td></tr>
<tr><td class="{get_class('hard_parse_pct')}">hard parse elapsed time</td>
<td class="r">{round(db_time_min*60*metrics['hard_parse_pct']/100, 1)}</td>
<td class="r">{metrics['hard_parse_pct']}</td></tr>
<tr><td>PL/SQL execution elapsed time</td><td class="r">{round(db_time_min*60*0.15, 1)}</td><td class="r">15.0</td></tr>
</table>
</div>'''
        
        # Memory section
        memory_html = f'''<div class="sec">
<h2>Memory Statistics</h2>
<table>
<tr><th>Metric</th><th class="r">Value</th></tr>
<tr><td>SGA Size (MB):</td><td class="r">{metrics['sga_size']}</td></tr>
<tr><td>PGA Allocated (MB):</td><td class="r {get_class('pga_allocated')}">{metrics['pga_allocated']}</td></tr>
<tr><td>PGA Used (MB):</td><td class="r {get_class('pga_used')}">{metrics['pga_used']}</td></tr>
<tr><td>PGA Usage %:</td><td class="r {get_class('pga_usage_pct')}">{pga_usage_pct}</td></tr>
<tr><td class="{get_class('sorts_disk')}">Sorts in Memory:</td>
<td class="r">{metrics['sorts_memory']:,}</td></tr>
<tr><td class="{get_class('sorts_disk')}">Sorts on Disk:</td>
<td class="r">{metrics['sorts_disk']:,}</td></tr>'''
        
        if anomaly_type == 'TEMP_SPACE' and 'temp_space_used' in metrics:
            memory_html += f'''<tr><td class="anom">Temp Space Used (MB):</td><td class="r">{metrics['temp_space_used']:,}</td></tr>'''
        
        memory_html += '</table>\n</div>'
        
        # System Statistics section
        system_html = f'''<div class="sec">
<h2>Operating System Statistics</h2>
<table>
<tr><th>Metric</th><th class="r">Value</th></tr>
<tr><td class="{get_class('os_cpu_usage')}">OS CPU Usage %:</td>
<td class="r">{metrics['os_cpu_usage']}</td></tr>
<tr><td class="{get_class('load_average')}">Load Average:</td>
<td class="r">{metrics['load_average']}</td></tr>
<tr><td>Physical Memory (GB):</td><td class="r">16</td></tr>
<tr><td>Num CPUs:</td><td class="r">{random.choice([4, 8, 16, 32])}</td></tr>
</table>
</div>'''
        
        # Tablespace I/O Stats section
        tablespace_html = f'''<div class="sec">
<h2>Tablespace I/O Stats</h2>
<table>
<tr><th>Tablespace</th><th class="r">Reads</th><th class="r">Writes</th><th class="r">Read Time (s)</th><th class="r">Write Time (s)</th></tr>
<tr><td>SYSTEM</td><td class="r">{random.randint(1000, 5000):,}</td><td class="r">{random.randint(500, 2000):,}</td>
<td class="r">{round(random.uniform(2, 10), 1)}</td><td class="r">{round(random.uniform(1, 5), 1)}</td></tr>
<tr><td>SYSAUX</td><td class="r">{random.randint(800, 3000):,}</td><td class="r">{random.randint(400, 1500):,}</td>
<td class="r">{round(random.uniform(1, 8), 1)}</td><td class="r">{round(random.uniform(0.5, 4), 1)}</td></tr>
<tr><td>USERS</td><td class="r">{random.randint(5000, 15000):,}</td><td class="r">{random.randint(2000, 8000):,}</td>
<td class="r">{round(random.uniform(5, 25), 1)}</td><td class="r">{round(random.uniform(3, 15), 1)}</td></tr>
<tr><td>TEMP</td><td class="r">{random.randint(500, 3000):,}</td><td class="r">{random.randint(300, 2000):,}</td>
<td class="r">{round(random.uniform(1, 6), 1)}</td><td class="r">{round(random.uniform(0.5, 4), 1)}</td></tr>
</table>
</div>'''
        
        # Segment Statistics section
        segment_html = f'''<div class="sec">
<h2>Segments by Physical Reads</h2>
<table>
<tr><th>Owner</th><th>Object Name</th><th>Object Type</th><th class="r">Physical Reads</th></tr>
<tr><td>APPUSER</td><td>ORDERS</td><td>TABLE</td><td class="r">{random.randint(5000, 20000):,}</td></tr>
<tr><td>APPUSER</td><td>CUSTOMERS</td><td>TABLE</td><td class="r">{random.randint(3000, 15000):,}</td></tr>
<tr><td>APPUSER</td><td>ORDER_ITEMS</td><td>TABLE</td><td class="r">{random.randint(4000, 18000):,}</td></tr>
<tr><td>APPUSER</td><td>IDX_ORD_DATE</td><td>INDEX</td><td class="r">{random.randint(2000, 10000):,}</td></tr>
<tr><td>APPUSER</td><td>PRODUCTS</td><td>TABLE</td><td class="r">{random.randint(2500, 12000):,}</td></tr>
</table>
</div>'''
        
        # Build complete HTML
        html = f'''<!DOCTYPE html>
<html><head>
<meta charset="utf-8">
<title>AWR Report {db_name}</title>
<style>
body{{font:10pt Courier;background:#fff;margin:15px}}
.hdr{{background:#036;color:#fff;padding:15px;border:2px solid #000;margin-bottom:15px}}
.sec{{background:#f9f9f9;padding:12px;margin:10px 0;border:1px solid #999}}
table{{width:100%;border-collapse:collapse;margin:8px 0;font-size:9pt}}
th{{background:#ccc;padding:6px;border:1px solid #999;font-weight:bold;text-align:left}}
td{{padding:5px;border:1px solid #ddd}}
tr:nth-child(even){{background:#f5f5f5}}
.r{{text-align:right}}
.anom{{color:#c00;font-weight:bold}}
.warn{{color:#f60}}
h2{{color:#036;border-bottom:1px solid #000;padding-bottom:3px;font-size:11pt;margin:12px 0 6px}}
</style>
</head><body>

<div class="hdr">
<strong>WORKLOAD REPOSITORY Report</strong><br><br>
DB Name: {db_name} | DB Id: {db_id} | Instance: {instance}<br>
Period: {start_time.strftime('%Y-%m-%d %H:%M:%S')} to {end_time.strftime('%Y-%m-%d %H:%M:%S')}<br>
Elapsed: {elapsed_min:.2f} min | DB Time: {db_time_min:.2f} min
</div>

<div class="sec">
<h2>Load Profile</h2>
<table>
<tr><th>Metric</th><th class="r">Per Second</th><th class="r">Per Transaction</th></tr>
<tr><td>DB Time(s):</td><td class="r {get_class('db_time_per_sec')}">{metrics['db_time_per_sec']}</td><td class="r">{db_time_per_txn}</td></tr>
<tr><td>DB CPU(s):</td><td class="r">{metrics['db_cpu_per_sec']}</td><td class="r">{db_cpu_per_txn}</td></tr>
<tr><td>Redo size:</td><td class="r">{metrics['redo_size']:,}</td><td class="r">{redo_per_txn:,}</td></tr>
<tr><td>Logical reads:</td><td class="r">{metrics['logical_reads']:,}</td><td class="r">{logical_per_txn:,}</td></tr>
<tr><td>Physical reads:</td><td class="r {get_class('physical_reads')}">{metrics['physical_reads']:,}</td><td class="r">{physical_per_txn:,}</td></tr>
<tr><td>Executes:</td><td class="r">{metrics['executes']}</td><td class="r">{exec_per_txn}</td></tr>
<tr><td>Transactions:</td><td class="r">{metrics['transactions']}</td><td class="r">1.00</td></tr>
</table>
</div>

<div class="sec">
<h2>Instance Efficiency (Target 100%)</h2>
<table>
<tr><th>Metric</th><th class="r">Value</th></tr>
<tr><td>Buffer Hit %:</td><td class="r {get_class('buffer_hit')}">{metrics['buffer_hit']}</td></tr>
<tr><td>Library Hit %:</td><td class="r">{metrics['library_hit']}</td></tr>
<tr><td>Soft Parse %:</td><td class="r">{metrics['soft_parse']}</td></tr>
<tr><td>Latch Hit %:</td><td class="r {get_class('latch_hit')}">{metrics['latch_hit']}</td></tr>
</table>
</div>

<div class="sec">
<h2>Top Foreground Events by Wait Time</h2>
<table>
<tr><th>Event</th><th class="r">Waits</th><th class="r">Time (s)</th><th class="r">Avg (ms)</th><th class="r">% DB</th></tr>
{wait_events_html}
</table>
</div>

{time_model_html}

{memory_html}

{system_html}

{tablespace_html}

{segment_html}

<div class="sec">
<h2>SQL ordered by Elapsed Time</h2>
<table>
<tr><th>SQL ID</th><th class="r">Execs</th><th class="r">Elapsed (s)</th><th class="r">CPU (s)</th><th>SQL Text</th></tr>
{sql_section}
</table>
</div>

<div class="sec">
<p><strong>Report Type:</strong> {anomaly_type}<br>
<strong>Report Number:</strong> {report_num}<br>
<strong>Generated:</strong> {datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]}Z</p>
</div>

</body></html>'''
        
        return html


# Main execution
if __name__ == "__main__":
    print("=" * 70)
    print("AWR Report Generator for Database Health Analysis")
    print("=" * 70)
    print()
    
    generator = AWRReportGenerator()
    
    # Generate reports (default: 300)
    # You can change the count parameter: generator.generate_reports(count=500)
    output_directory = generator.generate_reports(count=300)
    
    print()
    print("=" * 70)
    print("Generation Complete!")
    print("=" * 70)
    print(f"\nReports saved to: {output_directory}")
    print("\nNext Steps:")
    print("1. Run AWR parser to extract metrics")
    print("2. Create feature engineering pipeline")
    print("3. Train anomaly detection models")
    print("\nAnomaly Types Generated:")
    print("  - NORMAL (80%)")
    print("  - CPU_SPIKE")
    print("  - MEMORY_PRESSURE")
    print("  - IO_BOTTLENECK")
    print("  - LOCK_CONTENTION")
    print("  - TEMP_SPACE")
    print("  - NETWORK_LATENCY")
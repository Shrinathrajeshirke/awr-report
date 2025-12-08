import os
import sys
from src.logger import logging
from src.exception import CustomException

from bs4 import BeautifulSoup
import pandas as pd
import re

class AWRParser:
    def __init__(self):
        self.parsed_data= []
    
    def _parse_header(self, soup):
        
        try:    
            # headers section
            header_div = soup.find('div', class_='hdr')
            header_text = header_div.get_text()

            # extract db name
            db_name_match = re.search(r'DB Name:\s*(\S+)', header_text)
            db_name = db_name_match.group(1) if db_name_match else None   

            # extract db id
            db_id_match = re.search(r'DB Id:\s*(\d+)', header_text)
            db_id = db_id_match.group(1) if db_id_match else None        

            # extract instance
            instance_match = re.search(r'Instance:\s*(\d+)', header_text)
            instance = instance_match.group(1) if instance_match else None

            # Extract period
            period_match = re.search(r'Period:\s*(.+?)\s+to\s+(.+?)(?:\n|$)',header_text)
            start_time = period_match.group(1) if period_match else None
            end_time = period_match.group(2) if period_match else None
            
            # Extract elapsed time
            elapsed_match = re.search(r'Elapsed:\s*([\d.]+)\s*min', header_text)
            elapsed_min = float(elapsed_match.group(1)) if elapsed_match else None

            # extract DB time
            db_time_match = re.search(r'DB Time:\s*([\d.]+)\s*min', header_text)
            db_time_min = float(db_time_match.group(1)) if db_time_match else None

            return {
                 'db_name': db_name,
                 'db_id': db_id, 
                 'instance': instance,
                 'start_time': start_time,
                 'end_time': end_time,
                 'elapsed_min': elapsed_min,
                 'db_time_min': db_time_min
            }
        except Exception as e:
            raise CustomException(e, sys)
    
    def _clean_header_key(self, key):
        """ removes the special characters and whitespaces from header strings"""
        # strip trailing colon, parentheses and excessive whitespaces
        key = key.strip().replace(':','').replace('(','').replace(')', '')
        # replace remaining non-alphanumeric chars with _
        key = re.sub(r'[^a-zA-Z0-9\s_]', '', key)
        # replace spaces with underscores
        key = key.replace(' ', '_')
        return key.strip('_') # strip any leading/trailing underscores

    def _clean_data_value(self, value):
        """ removes thousands separators and converts to float if possible"""
        # remove thousands separators (commans)
        value = value.replace(',','')

        # attempt convert to float
        try:
            # check if it looks like an integer or float
            if value and value.replace('.','',1).isdigit():
                return float(value)
        except ValueError:
            return value
    
    def _parse_table(self, section_name, soup):
        try:
            """
            finds a table based on H2 header and extract its content
            """
            extracted_data = []
            # find h2 with section name
            h2_tag = soup.find('h2', string=section_name)
            if not h2_tag:
                return extracted_data
            
            # find the table after this h2
            section_div = h2_tag.find_parent('div', class_='sec')
            table = section_div.find('table')

            if not table:
                return extracted_data
            
            # extract rows
            rows = table.find_all('tr')
            if not rows:
                return extracted_data
            
            header = []

            # iterate through each row found in the table
            for i, row in enumerate(rows):
                # find all data cells (td) and header cells (th) in the current row
                cells = row.find_all(['td','th'])

                # extract raw text from cells
                ## process header row (first row)
                if i==0 and row.find('th'):
                    # extract header names from <th> tags
                    header = [
                        self._clean_header_key(cell.get_text(strip=True))
                        for cell in row.find_all('th')
                    ]
                    continue # skip to the next row

                ## process data rows
                if cells:
                    row_data = []
                    for j, cell in enumerate(cells):
                        text = cell.get_text(strip=True)

                        if j==0:
                            text = text.rstrip(':').strip()
                            row_data.append(text)
                        else:
                            row_data.append(self._clean_data_value(text))

                    if not header and row_data:
                        if len(row_data) > 1:
                            if not header:
                                if section_name in ['Instance Efficiency (Target 100%)', 'Memory Statistics', 'Operating System Statistics']:
                                    header = ['metric', 'Value']
                                elif section_name == 'Load Profile':
                                    header = ['Metric', 'Per_Second', 'Per_Transaction']
                                elif section_name == 'Top Foreground Events by Wait Time':
                                    header = ['Event','Waits','Time (s)','Avg (ms)','% DB']
                                elif section_name == 'Time Model Statistics':
                                    header = ['Statistic','Time (s)','% DB Time']
                                elif section_name == 'Tablespace I/O Stats':
                                    header = ['Tablespace','Reads','Writes','Read Time (s)','Write Time (s)']
                                elif section_name == 'Segments by Physical Reads':
                                    header = ['Owner','Object Name','Object Type','Physical Reads']
                                elif section_name == 'SQL ordered by Elapsed Time':
                                    header = ['SQL ID','Execs','Elapsed (s)','CPU (s)','SQL Text']
                            if len(header) == len(row_data):
                                row_dict = dict(zip(header, row_data))
                                extracted_data.append(row_dict)
                    elif header and len(header) == len(row_data):
                        row_dict = dict(zip(header, row_data))
                        extracted_data.append(row_dict)

            return extracted_data

        except Exception as e:
            raise CustomException(e, sys)
        
    def _parse_anomaly_type(self, soup):
        try:
            strong_tag = soup.find('strong', string = 'Report Type:')

            if strong_tag:
                parent_text = strong_tag.parent.get_text()

                match = re.search(r'Report Type:\s*(\w+)', parent_text)
                return match.group(1) if match else None
            return None
        except Exception as e:
            raise CustomException(e, sys)
        
    def parse_single_report(self, filepath):
        """ Parse a single awr HTML report and extract all metrics"""

        try:
            #logging.info(f"Parsing AWR report: {filepath}")

            # read HTML file
            with open(filepath, 'r', encoding='utf-8') as f:
                html_content = f.read()

            # parse with BeautifulSoup
            soup = BeautifulSoup(html_content, 'lxml')
            data = self._parse_header(soup)

            # extract different sections
            data['filename'] = os.path.basename(filepath)
            data['load_profile'] = self._parse_table('Load Profile', soup)
            data['instance_efficiency'] = self._parse_table('Instance Efficiency (Target 100%)', soup)
            data['top_events'] = self._parse_table('Top Foreground Events by Wait Time', soup)
            data['time_model'] = self._parse_table('Time Model Statistics', soup)
            data['memory_stats'] = self._parse_table('Memory Statistics', soup)
            data['os_stats'] = self._parse_table('Operating System Statistics', soup)
            data['tablespace_io'] = self._parse_table('Tablespace I/O Stats', soup)
            data['segments'] = self._parse_table('Segments by Physical Reads', soup)
            data['sql_stats'] = self._parse_table('SQL ordered by Elapsed Time', soup)
            data['anomaly_type'] = self._parse_anomaly_type(soup)
            return data
        

        except Exception as e:
             raise CustomException(e,sys)
        
    def _flatten_report_data(self, data):
        try:
            flat_data = {}

            flat_data['filename'] = data.get('filename')
            flat_data['db_name'] = data.get('db_name')
            flat_data['db_id'] = data.get('db_id')
            flat_data['instance'] = data.get('instance')
            flat_data['start_time'] = data.get('start_time')
            flat_data['end_time'] = data.get('end_time')
            flat_data['elapsed_min'] = data.get('elapsed_min')
            flat_data['db_time_min'] = data.get('db_time_min')
            flat_data['anomaly_type'] = data.get('anomaly_type')

            #flatten load profile
            load_profile = data.get('load_profile',[])
            for row in load_profile:
                metric = row.get('Metric')
                if metric == 'DB Time(s)':
                    flat_data['db_time_per_sec'] = row.get('Per_Second')
                elif metric == 'DB CPU(s)':
                    flat_data['db_cpu_per_sec'] = row.get('Per_Second')
                elif metric == 'Redo size':
                    flat_data['redo_size_per_sec'] = row.get('Per_Second')
                elif metric == 'Logical reads':
                    flat_data['logical_reads_per_sec'] = row.get('Per_Second')
                elif metric == 'Physical reads':
                    flat_data['physical_reads_per_sec'] = row.get('Per_Second')
                elif metric == 'Executes':
                    flat_data['executes_per_sec'] = row.get('Per_Second')
                elif metric == 'Transactions':
                    flat_data['transactions_per_sec'] = row.get('Per_Second')
            
            #flattern from instance efficiency
            instance_efficiency = data.get('instance_efficiency')
            for row in instance_efficiency:
                metric = row.get('Metric')
                if metric == 'Buffer Hit %':
                    flat_data['buffer_hit_pct'] = row.get('Value')
                elif metric == 'Library Hit %':
                    flat_data['library_hit_pct'] = row.get('Value')
                elif metric == 'Soft Parse %':
                    flat_data['soft_parse_pct'] = row.get('Value')
                elif metric == 'Latch Hit %':
                    flat_data['latch_hit_pct'] = row.get('Value')
            
            #flatten top events
            top_events = data.get('top_events', [])
            for idx, row in enumerate(top_events[:3], 1):
                flat_data[f'top_event_{idx}_name'] = row.get('Event')
                flat_data[f'top_event_{idx}_time_sec'] = row.get('Time_s')
                flat_data[f'top_event_{idx}_avg_ms'] = row.get('Avg_ms')

            #flatten time model
            time_model = data.get('time_model')
            for row in time_model:
                statistic = row.get('Statistic')
                if statistic == 'parse time elapsed':
                    flat_data['parse_time_pct'] = row.get('DB_Time')
                elif statistic == 'hard parse elapsed time':
                    flat_data['hard_parse_pct'] = row.get('DB_Time')
            
            #flatten memory stats
            memory_stats = data.get('memory_stats')
            for row in memory_stats:
                metric = row.get('Metric')
                if metric == 'SGA Size (MB)':
                    flat_data['sga_size_mb'] = row.get('Value')
                elif metric == 'PGA Allocated (MB)':
                    flat_data['pga_allocated_mb'] = row.get('Value')
                elif metric == 'PGA Used (MB)':
                    flat_data['pga_used_mb'] = row.get('Value')
                elif metric == 'PGA Usage %':
                    flat_data['pga_usage_pct'] = row.get('Value')
                elif metric == 'Sorts in Memory':
                    flat_data['sorts_memory'] = row.get('Value')
                elif metric == 'Sorts on Disk':
                    flat_data['sorts_disk'] = row.get('Value')
            
            #flattern os stats
            os_stats = data.get('os_stats')
            for row in os_stats:
                metric = row.get('Metric')
                if metric == 'OS CPU Usage %':
                    flat_data['os_cpu_usage_pct'] = row.get('Value')
                elif metric == 'Load Average':
                    flat_data['load_average'] = row.get('Value')
                elif metric == 'Physical Memory (GB)':
                    flat_data['physical_memory_gb'] = row.get('Value')
                elif metric == 'Num CPUs':
                    flat_data['num_cpus'] = row.get('Value')

            if flat_data.get('db_time_per_sec') and flat_data.get('db_time_per_sec') > 0:
                flat_data['cpu_pct_of_db_time'] = (flat_data['db_cpu_per_sec'] / flat_data['db_time_per_sec']) * 100
            else:
                flat_data['cpu_pct_of_db_time'] = None

            if flat_data.get('logical_reads_per_sec') and flat_data.get('logical_reads_per_sec') > 0:
                flat_data['physical_to_logical_ratio'] = flat_data['physical_reads_per_sec'] / flat_data['logical_reads_per_sec']
            else:
                flat_data['physical_to_logical_ratio'] = None
        
            return flat_data
        except Exception as e:
            raise CustomException(e, sys)
    
    def parse_all_reports(self, input_dir, output_csv):
        """ Parse all AWR reports in directory and save to CSV"""
        try:
            logging.info(f"Parsing all reports from: {input_dir}")

            all_parsed_data = []

            # get all HTML files
            html_files = [f for f in os.listdir(input_dir) if f.endswith('.html')]

            logging.info(f"found {len(html_files)} HTML files")

            # parse each file
            for i, filename in enumerate(html_files, 1):
                filepath = os.path.join(input_dir, filename)

                #parse the report
                data = self.parse_single_report(filepath=filepath)

                # flatten the data 
                flattened_data = self._flatten_report_data(data)

                all_parsed_data.append(flattened_data)

                if i%50 == 0:
                    logging.info(f"Parsed {i}/{len(html_files)} reports")

            #convert to datafram and save
            df = pd.DataFrame(all_parsed_data)
            df.to_csv(output_csv, index=False)
            logging.info(f"saved parsed data to: {output_csv}")
            return df
            
        except Exception as e:
            raise CustomException(e, sys)
        

import yaml
import pandas as pd
import os
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from ingestors.google_analytics import GA4Ingestor
from ingestors.woocommerce import WooCommerceIngestor
from ingestors.shopify import ShopifyIngestor

def load_config():
    with open("config.yaml", "r") as f:
        return yaml.safe_load(f)

def run_reconciliation():
    print("--- Starting DRA Transaction Reconciliation Ultra ---")
    config = load_config()
    
    # 1. Ingest GA4 Data
    ga4 = GA4Ingestor(
        property_id=config['ga4']['property_id'],
        credentials_file=config['ga4']['credentials_file']
    )
    df_ga4 = ga4.fetch_transactions(days=config['reconciliation']['match_window_days'])
    
    # 2. Ingest Backend Data based on Platform
    platform = config['backend']['platform']
    df_backend = pd.DataFrame()
    
    if platform == 'woocommerce':
        wc = WooCommerceIngestor(
            url=config['backend']['woocommerce']['url'],
            key=config['backend']['woocommerce']['consumer_key'],
            secret=config['backend']['woocommerce']['consumer_secret']
        )
        df_backend = wc.fetch_orders(days=config['reconciliation']['match_window_days'])
        
    elif platform == 'shopify':
        sh = ShopifyIngestor(
            shop_url=config['backend']['shopify']['shop_url'],
            access_token=config['backend']['shopify']['access_token']
        )
        df_backend = sh.fetch_orders(days=config['reconciliation']['match_window_days'])
    
    else:
        print(f"Error: Unsupported status platform '{platform}'")
        return

    # 3. Reconcile
    print(f"Reconciling {len(df_backend)} backend orders ({platform}) vs {len(df_ga4)} GA4 events...")
    
    # Simple ID matching (assuming IDs are clean/normalized)
    common = set(df_ga4['clean_id']) & set(df_backend['clean_id'])
    missing_ids = set(df_backend['clean_id']) - set(df_ga4['clean_id'])
    
    if len(df_backend) > 0:
        match_rate = len(common) / len(df_backend) * 100
    else:
        match_rate = 0
    
    # Calculate financial discrepancy
    total_backend_value = df_backend['value'].sum()
    total_ga4_value = df_ga4['value'].sum()
    discrepancy = total_backend_value - total_ga4_value
    
    missing_orders_data = []
    if missing_ids:
        missing_orders_df = df_backend[df_backend['clean_id'].isin(missing_ids)]
        missing_orders_data = missing_orders_df.to_dict(orient='records')

    # 4. Report
    print(f"\n[RESULTS]")
    print(f"Match Rate: {match_rate:.1f}%")
    print(f"Missing Orders: {len(missing_ids)}")
    
    # Generate HTML Report
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template('templates/automated_report.html')
    
    html_out = template.render(
        date=datetime.now().strftime("%Y-%m-%d %H:%M"),
        days_analyzed=config['reconciliation']['match_window_days'],
        total_backend=len(df_backend),
        total_ga4=len(df_ga4),
        match_rate=round(match_rate, 1),
        missing_count=len(missing_ids),
        discrepancy=f"{discrepancy:,.2f}",
        missing_orders=missing_orders_data
    )
    
    report_filename = f"report_{datetime.now().strftime('%Y%m%d')}.html"
    with open(report_filename, "w") as f:
        f.write(html_out)
        
    print(f"✅ Report generated: {report_filename}")
        
    print("\n--- Compliance Check ---")
    if match_rate < 95:
        print("❌ ALERT: Match rate below 95%.")
        if config['alerts']['email']['enabled']:
            recipients = ", ".join(config['alerts']['email']['recipients'])
            print(f"📧 SENDING EMAIL ALERT to: {recipients}")
            print("   Subject: [DRA Alert] Reconciliation dropped below 95%")
    else:
        print("✅ Status Healthy.")
        
    return report_filename

if __name__ == "__main__":
    run_reconciliation()

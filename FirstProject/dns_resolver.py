import asyncio
import aiodns
from datetime import datetime

async def query_dns(target_domain, record_type, resolver):
    try:
        result = await resolver.query(target_domain, record_type)
        print(f"\n{record_type} records for {target_domain}:")
        detailed_output = []

        # Some responses are lists, others are single objects
        records = result if isinstance(result, list) else [result]

        for r in records:
            if record_type == 'A':
                info = f"IPv4 Address: {r.host}"
            elif record_type == 'AAAA':
                info = f"IPv6 Address: {r.host}"
            elif record_type == 'CNAME':
                info = f"Canonical Name: {r.cname}"
            elif record_type == 'MX':
                info = f"Mail Exchanger: {r.host}, Priority: {r.priority}"
            elif record_type == 'TXT':
                info = f"Text Record: {''.join(r.text)}"
            elif record_type == 'SOA':
                info = (
                    f"Primary NS: {r.nsname}, "
                    f"Responsible: {r.hostmaster}, "
                    f"Serial: {r.serial}, "
                    f"Refresh: {r.refresh}, "
                    f"Retry: {r.retry}, "
                    f"Expire: {r.expires}, "
                    f"Minimum TTL: {r.minttl}"
                )
            else:
                info = str(r)

            print(f" - {info}")
            detailed_output.append(info)

        return (record_type, detailed_output)

    except aiodns.error.DNSError as e:
        print(f"\n{record_type} records for {target_domain}: No records found ({e})")
        return (record_type, [])

async def main():
    target_domain = input("Enter the target domain (e.g., example.com): ").strip()
    if not target_domain:
        print("Error: No target domain provided.")
        return
    
    record_types = ['A', 'AAAA', 'CNAME', 'MX', 'TXT', 'SOA']
    resolver = aiodns.DNSResolver()

    tasks = [query_dns(target_domain, rtype, resolver) for rtype in record_types]
    results = await asyncio.gather(*tasks)

    log_file = f"dns_results_{target_domain.replace('.', '_')}.log"
    with open(log_file, "w") as f:
        f.write(f"DNS Query Results for {target_domain} - {datetime.now()}\n")
        for record_type, records in results:
            f.write(f"\n{record_type} Records:\n")
            if records:
                for record in records:
                    f.write(f" - {record}\n")
            else:
                f.write(" - No records found\n")
    print(f"\nResults have been logged to {log_file}")

if __name__ == "__main__":
    asyncio.run(main())

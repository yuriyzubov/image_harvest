from ftplib import FTP
from concurrent.futures import ThreadPoolExecutor
import os
import time

def get_file_size(file_name, ftp_host, ftp_dir):
    with FTP(ftp_host) as ftp:
        ftp.login(user='anonymous', passwd='')
        ftp.set_pasv(True)
        ftp.cwd(ftp_dir)
        size = ftp.size(file_name)
    return size

def download_chunk(start, end, chunk_index, output_file, ftp_host, ftp_dir, file_name):
    time.sleep(0.1)
    try:
        with FTP(ftp_host) as ftp:
            ftp.login(user='anonymous', passwd='')
            ftp.set_pasv(True)
            ftp.cwd(ftp_dir)
            ftp.sendcmd("TYPE I")  # binary mode

            ftp.sendcmd(f"REST {start}")
            with open(f"{output_file}.part{chunk_index}", 'wb') as f:
                def callback(data):
                    if f.tell() + len(data) <= (end - start):
                        f.write(data)
                    else:
                        # Trim overflow from the final chunk
                        remaining = end - start - f.tell()
                        f.write(data[:remaining])
                        raise StopIteration()

                try:
                    ftp.retrbinary(f"RETR {file_name}", callback)
                except StopIteration:
                    pass
            print(f"Chunk {chunk_index} done: {start}-{end}")
    except Exception as e:
        print(f"Chunk {chunk_index} failed: {e}")

def merge_chunks(total_chunks, output_file):
    with open(output_file, 'wb') as outfile:
        for i in range(total_chunks):
            with open(f"{output_file}.part{i}", 'rb') as infile:
                outfile.write(infile.read())
            os.remove(f"{output_file}.part{i}")
    print("Merged all chunks.")

def main():
        
    ftp_host = 'ftp.ebi.ac.uk'
    ftp_dir = '/pub/databases/IDR/idr0086-miron-micrographs/20200610-ftp/experimentD/Miron_FIB-SEM/Miron_FIB-SEM_processed/'
    file_name = 'Figure_S3B_FIB-SEM_U2OS_20x20x20nm_xy.tif'
    output_file = '../../data/Figure_S3B_FIB-SEM_U2OS_20x20x20nm_xy_1.tif'
    chunk_size = 3*1024 * 1024  # 3 MB chunks
    threads = 4
    
    file_size = get_file_size(file_name, ftp_host, ftp_dir)
    print(f"Total size: {file_size} bytes")
    ranges = [(i, min(i + chunk_size, file_size)) for i in range(0, file_size, chunk_size)]

    with ThreadPoolExecutor(max_workers=threads) as executor:
        for idx, (start, end) in enumerate(ranges):
            executor.submit(download_chunk, start, end, idx, output_file, ftp_host, ftp_dir, file_name)

    # Wait for threads to complete before merging chunks
    executor.shutdown(wait=True)
    merge_chunks(len(ranges), output_file)

if __name__ == "__main__":
    main()

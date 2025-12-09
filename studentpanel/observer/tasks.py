# # studentpanel/tasks.py
# import logging
# from celery import shared_task, group, chord
# from django.conf import settings

# import os
# from datetime import datetime
# from pathlib import Path
# logger = logging.getLogger(__name__)


# from .video_merge_handler import upload_to_bunnystream
# from datetime import datetime
# import traceback

# # Import your existing merge function (ensure correct path)
# # from .video_merge_handler import merge_videos, get_all_video_files_for_lead, chunk_list, ffmpeg_concat
# from .video_merge_handler import merge_videos
# from subprocess import CalledProcessError, PIPE, STDOUT
# import subprocess

# @shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, max_retries=3)
# def merge_videos_task(self, zoho_lead_id, interview_link_count=None):
#     """
#     Simple Celery wrapper that calls your merge_videos() function.
#     This preserves your existing logic exactly.
#     """
#     logger.info("[CELERY] merge_videos_task start for %s", zoho_lead_id)
#     try:
#         result = merge_videos(zoho_lead_id, interview_link_count)
#         logger.info("[CELERY] merge_videos_task completed for %s -> %s", zoho_lead_id, result)
#         return {"status": "ok", "result": result}
#     except Exception as exc:
#         logger.exception("[CELERY] merge_videos_task failed for %s", zoho_lead_id)
#         # re-raise to allow retry (autoretry_for will handle it)
#         raise

# # ---- Optional: Chunked merge pattern for parallel speed-up ----
# # If you have many videos (e.g., 12-18), chunk them and merge chunks in parallel.
# # NOTE: You need helper functions: get_all_video_files_for_lead(zoho_lead_id)
# # and a merge_chunk task that merges a small list into intermediate file.
# @shared_task(bind=True)
# def merge_chunk(self, zoho_lead_id, chunk_index, file_list):
#     """
#     Merge one chunk (list of absolute file paths) into an intermediate file.
#     Returns the intermediate file path.
#     """
#     uploads_folder = os.path.join(settings.UPLOADS_FOLDER, zoho_lead_id)  # or replicate your own logic
#     out_path = os.path.join(uploads_folder, f"chunk_{chunk_index}_merged.webm").replace("\\", "/")
#     logger.info("Merging chunk %s for %s into %s", chunk_index, zoho_lead_id, out_path)
#     # use your ffmpeg concat helper (ffmpeg_concat defined in video_merge_handler)
#     ffmpeg_concat(file_list, out_path)
#     return out_path

# @shared_task(bind=True)
# def concat_chunks(self, chunk_files, zoho_lead_id):
#     """
#     Final concatenation of chunk files into single merged_video.webm
#     """
#     uploads_folder = os.path.join(settings.UPLOADS_FOLDER, zoho_lead_id)
#     output_path = os.path.join(uploads_folder, "merged_video.webm").replace("\\", "/")
#     logger.info("Concatenating chunks for %s -> %s", zoho_lead_id, output_path)
#     ffmpeg_concat(chunk_files, output_path)
#     return output_path

# def start_chunked_merge(zoho_lead_id, chunk_size=6):
#     """
#     Kick off chunked merge: splits file list and runs chord(group(...), concat_chunks)
#     """
#     file_list = get_all_video_files_for_lead(zoho_lead_id)  # implement in video_merge_handler
#     chunks = list(chunk_list(file_list, chunk_size))

#     # build group of merge_chunk tasks
#     grp = group(merge_chunk.s(zoho_lead_id, idx, chunk) for idx, chunk in enumerate(chunks))
#     # when group finished -> concat_chunks will run with list of results
#     # chord(grp)(concat_chunks.s(zoho_lead_id))  # alternative
#     # return chord(grp)(concat_chunks.s(zoho_lead_id))
#     # If you prefer chain:
#     return chord(grp)(concat_chunks.s(zoho_lead_id))



# # @shared_task(bind=True)
# # def save_interview_video(self, file_bytes, file_name, zoho_lead_id, browser_name=None, browser_version=None):

# #     try:
# #         # ---- Correct upload directory (exactly like your working code) ----
# #         upload_dir = Path("static") / "uploads" / "interview_videos" / zoho_lead_id
# #         upload_dir.mkdir(parents=True, exist_ok=True)

# #         file_path = upload_dir / file_name

# #         # ---- Write video file ----
# #         with open(file_path, "wb") as f:
# #             f.write(file_bytes)

# #         # ---- Save Browser Log ----
# #         log_dir = Path("static") / "uploads" / "profile_photos" / zoho_lead_id
# #         log_dir.mkdir(parents=True, exist_ok=True)

# #         log_file = log_dir / "browser_info.txt"

# #         with open(log_file, "a", encoding="utf-8") as f:
# #             f.write("===== Browser Info =====\n")
# #             f.write(f"Browser Name: {browser_name}\n")
# #             f.write(f"Browser Version: {browser_version}\n")
# #             f.write(f"Captured At: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
# #             f.write("========================\n")

# #         return {
# #             "file_path": str(file_path),
# #             "browser_log": str(log_file)
# #         }

# #     except Exception as e:
# #         raise Exception(f"Failed to save interview video: {str(e)}")


# # for reference, the old version that uploaded to Bunny Stream directly:

# # @shared_task(bind=True)
# # def save_interview_video(self, file_bytes, file_name, zoho_lead_id,
# #                          browser_name=None, browser_version=None):

# #     try:
# #         # -----------------------------------
# #         # 1. Upload DIRECTLY to Bunny Stream
# #         # -----------------------------------


# #          # ---------------------------------------------------
# #         # 0. SAVE video LOCALLY first
# #         # ---------------------------------------------------
# #         local_video_dir = Path("static") / "uploads" / "interview_videos" / zoho_lead_id
# #         local_video_dir.mkdir(parents=True, exist_ok=True)

# #         local_video_path = local_video_dir / file_name

# #         with open(local_video_path, "wb") as f:
# #             f.write(file_bytes)

# #         print(f"[LOCAL SAVE] Video stored at: {local_video_path}")


# #         print("[CELERY] Uploading interview video to Bunny Stream...")
# #         bunny_response = upload_to_bunnystream(
# #             file_bytes=file_bytes,
# #             file_name=file_name,
# #             zoho_lead_id=zoho_lead_id
# #         )

# #         # bunny_response should return:
# #         # {
# #         #   "video_id": "...",
# #         #   "cdn_url": "...",
# #         #   "status": "success"
# #         # }

# #         # -----------------------------------
# #         # 2. Save Browser Log locally
# #         # -----------------------------------
# #         log_dir = Path("static") / "uploads" / "profile_photos" / zoho_lead_id
# #         log_dir.mkdir(parents=True, exist_ok=True)

# #         log_file = log_dir / "browser_info.txt"

# #         with open(log_file, "a", encoding="utf-8") as f:
# #             f.write("===== Browser Info =====\n")
# #             f.write(f"Browser Name: {browser_name}\n")
# #             f.write(f"Browser Version: {browser_version}\n")
# #             f.write(f"Captured At: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
# #             f.write("========================\n")

# #         # -----------------------------------
# #         # 3. Return Bunny Stream data
# #         # -----------------------------------
# #         return {
# #             "bunnystream_video_id": bunny_response.get("video_id"),
# #             "bunnystream_url": bunny_response.get("cdn_url"),
# #             "browser_log_path": str(log_file),
# #             "status": "uploaded"
# #         }

# #     except Exception as e:
# #         raise Exception(f"Failed to save/upload interview video: {str(e)}")



# # @shared_task(bind=True)
# # def save_interview_video(self, file_bytes, file_name, zoho_lead_id,
# #                          browser_name=None, browser_version=None):

 

# #     # ---------------------------------------------------
# #     # LOG FILE
# #     # ---------------------------------------------------
# #     log_dir = Path(settings.BASE_DIR) / "interview_logs" / zoho_lead_id
# #     log_dir.mkdir(parents=True, exist_ok=True)


# #     celery_log_file = log_dir / "celery_upload_log.txt"

# #     def log(msg):
# #         timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
# #         line = f"[{timestamp}] {msg}"
# #         print(line)
# #         with open(celery_log_file, "a", encoding="utf-8") as f:
# #             f.write(line + "\n")

# #     try:
# #         log("=== Celery upload task STARTED ===")
# #         log(f"Lead ID: {zoho_lead_id}")
# #         log(f"File Name: {file_name}")

# #         # ---------------------------------------------------
# #         # CHECK RAW BYTES BEFORE SAVING
# #         # ---------------------------------------------------
# #         if not isinstance(file_bytes, (bytes, bytearray)):
# #             log("❌ file_bytes is NOT raw bytes! Type: " + str(type(file_bytes)))
# #             raise Exception("file_bytes is not bytes → corrupted input")

# #         log(f"Received Bytes Length: {len(file_bytes)}")

# #         if len(file_bytes) < 500:  # Too small to be real WebM
# #             log("❌ Video file too small → likely corrupted / incomplete")
# #             raise Exception("Corrupted or empty video frame")

# #         # Check if file starts with WebM header
# #         # WebM usually starts with \x1A\x45\xDF\xA3 (EBML)
# #         header_hex = file_bytes[:20].hex().upper()
# #         log(f"File Header (first 20 bytes hex): {header_hex}")

# #         if not file_bytes.startswith(b"\x1A\x45\xDF\xA3"):
# #             log("⚠️ Warning: File does NOT start with WebM EBML header!")

# #         # ---------------------------------------------------
# #         # SAVE LOCALLY
# #         # ---------------------------------------------------
# #         local_video_path = log_dir / file_name

# #         with open(local_video_path, "wb") as f:
# #             f.write(file_bytes)

# #         log(f"[LOCAL SAVE] Video stored at: {local_video_path}")
# #         log(f"Local File Size: {local_video_path.stat().st_size} bytes")

# #         # ---------------------------------------------------
# #         # BUNNY UPLOAD
# #         # ---------------------------------------------------
# #         log("[CELERY] Uploading video to Bunny Stream...")

# #         bunny_response = upload_to_bunnystream(
# #             file_bytes=file_bytes,
# #             file_name=file_name,
# #             zoho_lead_id=zoho_lead_id
# #         )

# #         log(f"[BUNNY RESPONSE] {bunny_response}")

# #         # ---------------------------------------------------
# #         # BROWSER LOG
# #         # ---------------------------------------------------
# #         browser_log_dir = Path("static") / "uploads" / "profile_photos" / zoho_lead_id
# #         browser_log_dir.mkdir(parents=True, exist_ok=True)

# #         browser_log_path = browser_log_dir / "browser_info.txt"

# #         with open(browser_log_path, "a", encoding="utf-8") as f:
# #             f.write("===== Browser Info =====\n")
# #             f.write(f"Browser Name: {browser_name}\n")
# #             f.write(f"Browser Version: {browser_version}\n")
# #             f.write(f"Captured At: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
# #             f.write("========================\n")

# #         log("Browser info saved.")
# #         log("=== Celery upload task COMPLETED ===")

# #         return {
# #             "bunnystream_video_id": bunny_response.get("video_id"),
# #             "bunnystream_url": bunny_response.get("cdn_url"),
# #             "local_video_path": str(local_video_path),
# #             "celery_log_file": str(celery_log_file),
# #             "status": "uploaded"
# #         }

# #     except Exception as e:
# #         log("🔥 ERROR during upload")
# #         log(traceback.format_exc())
# #         raise

# def repair_webm(input_path, output_path):
#     """
#     Attempts to fix a corrupted WebM by re-encoding using FFmpeg.
#     """
#     try:
#         subprocess.run([
#             settings.FFMPEG_PATH,
#             "-y",  # overwrite
#             "-i", str(input_path),
#             "-c:v", "libvpx",
#             "-c:a", "libopus",
#             "-f", "webm",
#             str(output_path)
#         ], check=True)
#         return True
#     except subprocess.CalledProcessError as e:
#         print("❌ FFmpeg repair failed:", e)
#         return False

# @shared_task(bind=True)
# def save_interview_video(self, file_bytes, file_name, zoho_lead_id,
#                          browser_name=None, browser_version=None):

#     # ---------------------------------------------------
#     # LOG FILE SETUP
#     # ---------------------------------------------------
#     log_dir = Path(settings.BASE_DIR) / "interview_logs" / zoho_lead_id
#     log_dir.mkdir(parents=True, exist_ok=True)

#     celery_log_file = log_dir / "celery_upload_log.txt"

#     def log(msg):
#         timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#         line = f"[{timestamp}] {msg}"
#         print(line)
#         with open(celery_log_file, "a", encoding="utf-8") as f:
#             f.write(line + "\n")

#     try:
#         log("===== CELERY VIDEO UPLOAD STARTED =====")
#         log(f"Lead ID: {zoho_lead_id}")
#         log(f"Incoming File Name: {file_name}")
#         log(f"Browser: {browser_name} {browser_version}")

#         # ---------------------------------------------------
#         # BASIC VALIDATION
#         # ---------------------------------------------------
#         if not isinstance(file_bytes, (bytes, bytearray)):
#             log("❌ ERROR: file_bytes is NOT raw bytes!")
#             log(f"Type Received: {type(file_bytes)}")
#             raise Exception("Invalid file_bytes type (not bytes)")

#         file_length = len(file_bytes)
#         log(f"✔ Received Bytes Length: {file_length}")

#         if file_length < 1000:
#             log("❌ ERROR: Video bytes too small — corrupted or incomplete upload!")
#             raise Exception("Video file corrupted — too small")

#         # ---------------------------------------------------
#         # WEBM HEADER VALIDATION
#         # ---------------------------------------------------
#         header4 = file_bytes[:4]
#         header20_hex = file_bytes[:20].hex().upper()

#         log(f"Header First 4 Bytes: {header20_hex[:8]}")
#         log(f"Header First 20 Bytes (HEX): {header20_hex}")

#         # if not file_bytes.startswith(b'\x1A\x45\xDF\xA3'):
#         #     log("⚠️ WARNING: Missing EBML/WebM header!")
#         #     log("Possible reasons: Firefox bug, wrong MIME type, truncated upload")


#         if not file_bytes.startswith(b'\x1A\x45\xDF\xA3'):
#             log("⚠️ WARNING: Missing EBML/WebM header! Attempting repair via FFmpeg...")

#             repaired_path = local_video_path.with_name("repaired_" + file_name)
#             if repair_webm(local_video_path, repaired_path):
#                 log(f"✔ Repair successful, switching to repaired file: {repaired_path}")
#                 local_video_path = repaired_path
#             else:
#                 log("❌ Repair failed, continuing with original file")

#         # ---------------------------------------------------
#         # SAVE LOCAL COPY
#         # ---------------------------------------------------
#         local_video_path = log_dir / file_name
#         with open(local_video_path, "wb") as f:
#             f.write(file_bytes)

#         saved_size = local_video_path.stat().st_size
#         log(f"✔ Local File Saved: {local_video_path}")
#         log(f"Local Saved File Size: {saved_size} bytes")

#         if saved_size != file_length:
#             log("❌ ERROR: FILE SIZE MISMATCH! Saved file is different from received bytes!")
#             raise Exception("File size mismatch after saving")

#         # ---------------------------------------------------
#         # FFPROBE DIAGNOSTICS
#         # ---------------------------------------------------
#         log("Running FFprobe diagnostics…")

#         try:
#             probe_output = subprocess.check_output(
#                 ["ffprobe", "-hide_banner", "-loglevel", "error",
#                  "-show_streams", "-of", "json", str(local_video_path)],
#                 stderr=subprocess.STDOUT
#             ).decode()

#             log("✔ FFprobe Output:")
#             log(probe_output)

#         except Exception as ff_err:
#             log("❌ FFprobe FAILED — VIDEO INVALID OR CORRUPTED!")
#             log(str(ff_err))

#         # ---------------------------------------------------
#         # BUNNY STREAM UPLOAD
#         # ---------------------------------------------------
#         log("Uploading file to Bunny Stream…")

#         try:


#              # ---------------------------------------------------
#         # 0. SAVE video LOCALLY first
#         # ---------------------------------------------------
#             local_video_dir = Path("static") / "uploads" / "interview_videos" / zoho_lead_id
#             local_video_dir.mkdir(parents=True, exist_ok=True)

#             local_video_path = local_video_dir / file_name

#             with open(local_video_path, "wb") as f:
#                 f.write(file_bytes)

#             print(f"[LOCAL SAVE] Video stored at: {local_video_path}")



#             bunny_response = upload_to_bunnystream(
#                 file_bytes=file_bytes,
#                 file_name=file_name,
#                 zoho_lead_id=zoho_lead_id
#             )
#             log(f"✔ BUNNY RESPONSE: {bunny_response}")

#         except Exception as bunny_err:
#             log("❌ ERROR: Bunny Stream upload failed!")
#             log(str(bunny_err))
#             log(traceback.format_exc())
#             raise

#         # ---------------------------------------------------
#         # BROWSER ENVIRONMENT LOG
#         # ---------------------------------------------------
#         browser_log_dir = Path("static") / "uploads" / "profile_photos" / zoho_lead_id
#         browser_log_dir.mkdir(parents=True, exist_ok=True)

#         browser_log_path = browser_log_dir / "browser_info.txt"

#         with open(browser_log_path, "a", encoding="utf-8") as f:
#             f.write("===== Browser Info =====\n")
#             f.write(f"Browser Name: {browser_name}\n")
#             f.write(f"Browser Version: {browser_version}\n")
#             f.write(f"Captured At: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
#             f.write("========================\n")

#         log("✔ Browser info saved.")
#         log("===== CELERY VIDEO UPLOAD COMPLETED SUCCESSFULLY =====")

#         return {
#             "status": "uploaded",
#             "local_video_path": str(local_video_path),
#             "celery_log_file": str(celery_log_file),
#             "bunnystream_video_id": bunny_response.get("video_id"),
#             "bunnystream_url": bunny_response.get("cdn_url"),
#         }

#     except Exception as e:
#         log("🔥 FATAL ERROR DURING VIDEO UPLOAD")
#         log(str(e))
#         log(traceback.format_exc())
#         raise



# # ============================================================
# # 2️⃣ SAVE CHUNKED VIDEO FILES (Correct Directory)
# # ============================================================

# @shared_task(bind=True)
# def save_uploaded_chunk(self, file_bytes, file_name, question_id, chunk_index):

#     try:
#         # ---- Correct chunk upload location ----
#         upload_dir = Path("static") / "uploads" / "interview_chunks" / str(question_id)
#         upload_dir.mkdir(parents=True, exist_ok=True)

#         # Chunk filename: chunk_1.webm, chunk_2.webm, etc.
#         chunk_path = upload_dir / f"chunk_{chunk_index}.webm"

#         with open(chunk_path, "wb") as f:
#             f.write(file_bytes)

#         return str(chunk_path)

#     except Exception as e:
#         raise Exception(f"Failed to save chunk: {str(e)}")
import time
import re
import logging
import os
from collections import defaultdict
from django_extensions.management.jobs import MinutelyJob
from studentpanel.models.student_interview_answer import StudentInterviewAnswers
from studentpanel.models.interview_process_model import Students
from gpt4all import GPT4All  
from adminpanel.common_imports import CommonQuestion

# Set up logging
logger = logging.getLogger(__name__)

class Job(MinutelyJob):
    help = "Runs every 2 minutes"

    def execute(self):
        logger.info("Starting job: Fetching student answers...")

        # Fetch all student answers
        student_answers = StudentInterviewAnswers.objects.all()

        if not student_answers.exists():
            logger.info("No student records found.")
            return

        model_path = "C:/Users/angel/Ascencia_Interviews/ascencia_interviews/studentpanel/models/mistral-7b-instruct-v0.2.Q2_K.gguf"
        
        # ✅ Check if the AI model file exists
        if not os.path.exists(model_path):
            logger.error("AI model path does not exist.")
            return

        final_results = []
        
        try:
            logger.info("Loading AI Model...")
            model = GPT4All(model_path)
            logger.info("Model loaded successfully!")

            # Dictionaries for storing scores
            student_scores = defaultdict(int)
            student_question_count = defaultdict(int)
            student_sentiment = defaultdict(int)
            student_grammar = defaultdict(int)

            # Fetch all questions in a single query
            question_map = {q.id: q for q in CommonQuestion.objects.all()}

            for student_answer in student_answers:
                student_id = student_answer.zoho_lead_id
                question_id = student_answer.question_id
                answer = student_answer.answer_text.strip()

                if not student_id or not question_id or not answer:
                    continue

                student_question_count[student_id] += 1  

                if question_id not in question_map:
                    logger.warning(f"Question ID {question_id} not found in database.")
                    continue

                question_data = question_map[question_id]

                # 🔹 Check Student Name for Question ID 1
                if question_id == 1:
                    possible_names = re.findall(r'\b[A-Z][a-z]*\b', answer)
                    student_data = Students.objects.filter(zoho_lead_id=student_id).values("first_name").first()
                    if student_data:
                        actual_first_name = student_data["first_name"]
                        if actual_first_name not in possible_names:
                            final_results.append({
                                "student_id": student_id,
                                "question_id": question_id,
                                "total_questions": student_question_count[student_id],
                                "overall_score": student_scores[student_id],
                                "status": "No matching name found",
                            })
                            continue  

                # 🔹 Check Program Name for Question ID 2
                if question_id == 2:
                    student_program = Students.objects.filter(zoho_lead_id=student_id).values("program").first()
                    if student_program:
                        program_name = student_program["program"].strip()
                        if not re.search(rf"\b{re.escape(program_name)}\b", answer, re.IGNORECASE):
                            final_results.append({
                                "student_id": student_id,
                                "question_id": question_id,
                                "total_questions": student_question_count[student_id],
                                "overall_score": student_scores[student_id],
                                "status": "Program name mismatch",
                            })
                            continue

                # ✅ AI Evaluation Prompt
                prompt = f"""
                You are an AI evaluator for university applications.  
                Your task is to **evaluate answers based on meaning, not just grammar.**  

                **Evaluation Criteria:**
                1️⃣ **Relevance to the question**  
                2️⃣ **Logical correctness**  
                3️⃣ **Grammar & clarity**  

                **Scoring Rules:**  
                - **1-2/10** → Completely incorrect or unrelated.  
                - **3-5/10** → Somewhat related but logically weak.  
                - **6-8/10** → Relevant but lacks details.  
                - **9-10/10** → Strong, detailed, and logical answer.  

                Now, evaluate the following answer:  
                **Question:** {question_data.question}  
                **Answer:** {answer}  

                Provide a score out of 10 and feedback in this format:  
                **Score: X/10**  
                **Feedback: [Your analysis]**  
                """

                try:
                    start_time = time.time()
                    response = model.generate(prompt)
                    end_time = time.time()
                    response_time = round(end_time - start_time, 2)

                    # 🔹 Extract score safely
                    match = re.search(r"Score:\s*(\d+)/10", response)
                    score = int(match.group(1)) if match else 0

                    # Store scores
                    student_scores[student_id] += score  
                    student_sentiment[student_id] += student_answer.sentiment_score  
                    student_grammar[student_id] += student_answer.grammar_accuracy  

                except Exception as ai_error:
                    logger.error(f"AI model evaluation error: {ai_error}")
                    continue

            # ✅ Prepare final results
            for student_id in student_scores.keys():
                total_questions = student_question_count[student_id]
                total_score = student_scores[student_id]

                final_results.append({
                    "student_id": student_id,
                    "total_score": total_score,  
                    "total_questions": total_questions,
                    "answer_score_percentage": (100 * total_score) / (total_questions * 10) if total_questions else 0,
                    "sentiment_score_percentage": (100 * student_sentiment[student_id]) / (total_questions * 10) if total_questions else 0,
                    "grammar_accuracy_percentage": (100 * student_grammar[student_id]) / (total_questions * 10) if total_questions else 0
                })

            logger.info(f"Final Results: {final_results}")

        except Exception as e:
            logger.error(f"Error in AI evaluation: {e}")

from nadeulAI_SSE.src import schemas
from nadeulAI_SSE.src.components.preprocessor import Preprocessor
from nadeulAI_SSE.src.components.scheduler import Scheduler
from pathlib import Path


def service(request: schemas.AssignRequest):
   current_file = Path(__file__).resolve()
   src_root = current_file.parents[1]
   db_path = src_root / "database" / "python_inner.db"

   preprocessor = Preprocessor(db_path=db_path)
   transformed_dto = preprocessor.transform(request)

   return transformed_dto


if __name__ == "__main__":
   request = schemas.AssignRequest(character=1,
                                   QA=["안녕하세요?", "반가워요", "잘지내요?"],
                                   mission_name="테스트용 미션 이름",
                                   submission_name="테스트용 서브 미션 이름",
                                   task_sequence=1)
   print(service(request))


   
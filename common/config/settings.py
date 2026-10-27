
from pathlib import Path
import os



from common.utility import(
    _resolve_environment ,
    _get_env_file,
    _load_settings,
    _get_key_data,
    _absolute,
    _require
)

from common.Models import (
    LoggingSettings,
    EmbeddingSettings,
    PineconeSettings,
    RagSettings,
    LlmSettings,
    WebSettings
)


class Settings:
   
    def __init__(self, path:str | Path | None = None):
        
        self.environment= _resolve_environment()
        env_file_path= _get_env_file(self.environment)
        
        self.setting_data= _load_settings(env_file_path)
        
        self.app_name = self.__load_app_name()
        self.log_settings = self.__load_log_settings()
        self.rag = self.__load_rag()
        self.llm = self.__load_llm()
        self.web = self.__load_web()

    def __load_app_name(self)->str:
        section =("common",)
        app_nm=str(
            _get_key_data(
                self.setting_data
                , section       # nested sections drill
                , "app_name"        # key for which data has to be extracted from setting_data
                , "agentic-ladder") # default if key's data not found
                )
        
        return app_nm 

    def __load_log_settings(self)->LoggingSettings:
        section = ("logging",)
        
        log_settings= LoggingSettings(
            dir=_absolute(str(_get_key_data(self.setting_data,section, "dir", "logs"))),
            file=str(_get_key_data(self.setting_data, section, "file", "app.log")),
            audit_file=str(_get_key_data(self.setting_data, section, "audit_file", "audit.log")),
            level=str(_get_key_data(self.setting_data,section, "level", "INFO")).upper(),
            console=bool(_get_key_data(self.setting_data,section, "console", True)),
            max_bytes=int(_get_key_data(self.setting_data,section, "max_bytes", 1_048_576)), # configure log rotation : the size limit per file 
            backup_count=int(_get_key_data(self.setting_data,section, "backup_count", 3)),  #  configure log rotation : how many rotated backups to keep.
        )

        return log_settings

    def __load_rag(self) -> RagSettings:
        rag = ("agent", "rag")      # agent.rag
        emb = (*rag, "embedding")   # agent.rag.embedding
        pine = (*rag, "pinecone")   # agent.rag.pinecone

        return RagSettings(
            resources_dir=_absolute(
                str(
                    _require(self.setting_data,rag, "resources_dir")
                )
            ),
           
            embedding=EmbeddingSettings(
                model=str(_require(self.setting_data,emb, "model")),
                dimensions=int(_require(self.setting_data,emb, "dimensions")),
                tokenizer_encoding=str(_require(self.setting_data,emb, "tokenizer_encoding")),
                chunk_size=int(_require(self.setting_data,emb, "chunk_size")),
                batch_size=int(_require(self.setting_data,emb, "batch_size")),
            ),
            
            pinecone=PineconeSettings(
                index_name=str(_require(self.setting_data,pine, "index_name")),
                namespace=str(_require(self.setting_data,pine, "namespace")),
            ),
        )

    def __load_llm(self) -> LlmSettings:
        llm = ("agent", "llm")
        return LlmSettings(
            model=str(_require(self.setting_data,llm, "model")),
            top_k=int(_require(self.setting_data,llm, "top_k")),
        )

    def __load_web(self) -> WebSettings:
        web = ("web_service",)
        return WebSettings(
            host=str(_require(self.setting_data,web, "host")),
            port=int(_require(self.setting_data,web, "port")),
        )
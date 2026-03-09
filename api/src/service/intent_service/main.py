from .rule_engine import rule_engine
from .semantic_search import semantic_search
from src.model.schema.intent_schema import RuleResult
from src.config.settings import setup_logging

logger = setup_logging()


class IntentService:
    
    def __init__(self):

        self.rule_engine = rule_engine

        self.semantic_search = semantic_search

    def process(self, user_input:str, intent_history:str) -> RuleResult:

        rule_engine_result: RuleResult = self.rule_engine.match_intent(user_input)

        logger.info(f"规则引擎输出:{rule_engine_result}")

        if rule_engine_result.intent != "unknown":
            return rule_engine_result

        llm_result: RuleResult = self.semantic_search.analyze(
            user_input=user_input,
            intent_history=intent_history,
            rule_result=rule_engine_result,
        )

        logger.info(f"语义检索服务结果:{llm_result}")
        return llm_result


intent_service = IntentService()

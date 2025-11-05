import pytest
from unittest.mock import patch
from src.chat_logic import get_seo_analysis_chain

@patch('src.chat_logic.api_integrations.get_psi_data')
@patch('src.chat_logic.seo_tools.analyze_readability')
@patch('src.chat_logic.TavilySearch')
def test_get_seo_analysis_chain_with_mocks(MockTavilySearch, MockAnalyzeReadability, MockGetPsiData):
    # Configurar os mocks
    mock_tavily_instance = MockTavilySearch.return_value
    mock_tavily_instance.invoke.return_value = "Resultados de busca falsos."
    MockAnalyzeReadability.return_value = 75.5
    MockGetPsiData.return_value = {"performance": "90", "accessibility": "95", "best_practices": "98", "seo": "100"}

    input_text = "Rascunho de um post sobre SEO"
    keyword = "SEO"
    url = "https://example.com"
    
    result = get_seo_analysis_chain(persona_prompt="Você é um especialista em SEO.", input_text=input_text, keyword=keyword, url=url)
    
    assert isinstance(result, dict)
    assert "answer" in result
    assert isinstance(result["answer"], str)
    
    # Verificar se as funções mockadas foram chamadas corretamente
    mock_tavily_instance.invoke.assert_called_with({"query": keyword})
    MockAnalyzeReadability.assert_called_with(input_text)
    MockGetPsiData.assert_called_with(url)

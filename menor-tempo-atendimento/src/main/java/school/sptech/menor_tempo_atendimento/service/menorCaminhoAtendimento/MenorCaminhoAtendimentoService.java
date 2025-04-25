package school.sptech.menor_tempo_atendimento.service.menorCaminhoAtendimento;

import com.fasterxml.jackson.databind.JsonNode;
import org.springframework.stereotype.Component;
import school.sptech.menor_tempo_atendimento.dto.MelhorCaminho;

@Component
public interface MenorCaminhoAtendimentoService {
    MelhorCaminho getMelhorCaminho(JsonNode jsonNode);
}

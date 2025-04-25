package school.sptech.menor_tempo_atendimento.controller;


import com.fasterxml.jackson.databind.JsonNode;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import school.sptech.menor_tempo_atendimento.dto.MelhorCaminho;
import school.sptech.menor_tempo_atendimento.service.menorCaminhoAtendimento.MenorCaminhoAtendimentoService;

@Controller
@RequestMapping("/grafos")
public class GrafoController {

    @Autowired
    private MenorCaminhoAtendimentoService menorCaminhoAtendimentoService;

    @PostMapping("/melhor-caminho")
    public ResponseEntity<MelhorCaminho> getMelhorCaminho(@RequestBody JsonNode jsonNode) {
        return ResponseEntity.ok(menorCaminhoAtendimentoService.getMelhorCaminho(jsonNode));
    }

}

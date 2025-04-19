package school.sptech.menor_tempo_atendimento.controller;


import com.fasterxml.jackson.databind.JsonNode;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import school.sptech.menor_tempo_atendimento.NoGrafo;
import school.sptech.menor_tempo_atendimento.domain.MelhorCaminho;
import school.sptech.menor_tempo_atendimento.service.GrafoService;

import java.util.List;

@Controller
@RequestMapping("/grafos")
public class GrafoController {

    @Autowired
    private GrafoService grafoService;

    @GetMapping("/melhor-caminho")
    public ResponseEntity<MelhorCaminho> getMelhorCaminho(@RequestBody JsonNode jsonNode) {
        grafoService.limparDados(); // Limpa tudo antes de começar
        System.out.println("JSON recebido:");
        System.out.println(jsonNode.toPrettyString());
        System.out.println("=============================================");
        grafoService.jsonToHashMap(jsonNode);
        grafoService.gerarNosGrafo(grafoService.hashMapToNografo());
        grafoService.gerarArestasGrafo();
        return ResponseEntity.ok(
                grafoService.caminhoOtimizado(grafoService.algoritmoDijkstra())
        );
    }

}

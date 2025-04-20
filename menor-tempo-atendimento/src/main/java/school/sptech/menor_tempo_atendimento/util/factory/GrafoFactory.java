package school.sptech.menor_tempo_atendimento.util.factory;

import com.fasterxml.jackson.databind.JsonNode;
import org.springframework.beans.factory.annotation.Autowired;
import school.sptech.menor_tempo_atendimento.service.GrafoService;
import school.sptech.menor_tempo_atendimento.util.Nivel;
import school.sptech.menor_tempo_atendimento.util.NoGrafo;
import school.sptech.menor_tempo_atendimento.util.Par;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class GrafoFactory {

    @Autowired
    private GrafoService grafoService;
    private HashMap<String, List<Par<String, Integer>>> valorArestaTransporteUpa;

    public GrafoFactory() {
        this.valorArestaTransporteUpa = new HashMap<>();
    }

    public HashMap<String, List<Par<String, Integer>>> jsonToHashMap(JsonNode upasProximas) {
        JsonNode upas = upasProximas.get("upas_proximas");
        for (JsonNode upa : upas) {
            String nome = upa.get("nome").asText();
            valorArestaTransporteUpa.putIfAbsent(nome, new ArrayList<>());
            JsonNode modos = upa.get("rotas");
            modos.fields().forEachRemaining(entry -> {
                String transporte = entry.getKey();
                String tempo = entry.getValue().get("Tempo Estimado").asText();

                valorArestaTransporteUpa.get(nome).add(new Par(transporte, Integer.parseInt(tempo.replaceAll("[^0-9]", ""))));
            });
        }

        return valorArestaTransporteUpa;
    }

    public List<NoGrafo> hashMapToNografo() {
        List<NoGrafo> listaAdicionarValoresGrafo = new ArrayList<>();
        int contador = 0;
        for (Map.Entry<String, List<Par<String, Integer>>> entry : valorArestaTransporteUpa.entrySet()) {
            String upa = entry.getKey();
            List<Par<String, Integer>> transporteTempo = entry.getValue();
            listaAdicionarValoresGrafo.add(new NoGrafo(upa, Nivel.NIVEL_UPA, 0));
            if (contador == 0) {
                for (Par<String, Integer> meioDeTransporteDaVez : transporteTempo) {
                    listaAdicionarValoresGrafo.add(new NoGrafo(meioDeTransporteDaVez.getChave(), Nivel.NIVEL_MEIO_DE_TRANSPORTE, 0));
                }
            }
            contador++;
        }
        return listaAdicionarValoresGrafo;
    }

    public void build(JsonNode jsonNode){
        grafoService.limparDados();
        grafoService.jsonToHashMap(jsonNode);
        grafoService.gerarNosGrafo(grafoService.hashMapToNografo());
        grafoService.gerarArestasGrafo(valorArestaTransporteUpa);
    }
}


package school.sptech.menor_tempo_atendimento.service.grafo;

import org.springframework.beans.factory.annotation.Autowired;
import school.sptech.menor_tempo_atendimento.dto.MelhorCaminho;
import school.sptech.menor_tempo_atendimento.service.upa.UpaService;
import school.sptech.menor_tempo_atendimento.util.Nivel;
import school.sptech.menor_tempo_atendimento.util.NoGrafo;
import school.sptech.menor_tempo_atendimento.util.Par;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class GrafoBuilder {


    private GrafoService grafoService;
    private UpaService upaService;
    private Map<NoGrafo, NoGrafo> rotaMedicos;
    private List<NoGrafo> listaUpas;
    private List<NoGrafo> meioDeTransporteUpas;
    private HashMap<String, List<Par<String, Integer>>> valorArestaTransporteUpa;

    @Autowired
    public GrafoBuilder(List<NoGrafo> meioDeTransporteUpas, HashMap<String, List<Par<String, Integer>>> valorArestaTransporteUpa
    ,GrafoService grafoService, UpaService upaService) {
        this.rotaMedicos = new HashMap<>();
        this.listaUpas = new ArrayList<>();
        this.meioDeTransporteUpas = meioDeTransporteUpas;
        this.valorArestaTransporteUpa = valorArestaTransporteUpa;
        this.grafoService = grafoService;
        this.upaService = upaService;
    }

    //Metodo para gerar o nos de maneira automatica
    //e nao precisar criando na mao
    //Paciente: Padrão -> ponto de inicio, não preciso de nenhuma info
    //MeioDeTransporte: Receber esses valores pela API do Maps
    //Upa: receber valores pela API do Maps (info de tempo do meio de transporte até a UPA)
    //tempo de espera: Receber valores pelo Banco de dados (info fornecida pela Visão computacional que nas UPAs)
    private void gerarNosGrafo() {
        NoGrafo paciente = new NoGrafo("paciente", Nivel.NIVEL_PACIENTE, 0);
        List<String> nomesUpas = new ArrayList<>();
        for (NoGrafo meioDeTransporte : meioDeTransporteUpas) {
            if (meioDeTransporte.getNivel() == Nivel.NIVEL_UPA) {
                nomesUpas.add(meioDeTransporte.getNome());
            }
        }
        List<NoGrafo> temposDeEspera = upaService.getTempoEspera(nomesUpas);
        grafoService.adicionarNo(paciente);
        for (NoGrafo meiosDeTranporteUpas : meioDeTransporteUpas) grafoService.adicionarNo(meiosDeTranporteUpas);
        for (NoGrafo tempoDeEspera : temposDeEspera) grafoService.adicionarNo(tempoDeEspera);
    }

    //Gerar as aresta do grafo de maneira automatica
    //para nao ter que criar na main na mao
    private void gerarArestasGrafo() {
        NoGrafo paciente = null;

        for (NoGrafo no : grafoService.adjacencia.keySet()) {
            if ("paciente".equals(no.getNome())) {
                paciente = no;
                break;
            }
        }
        for (NoGrafo no : grafoService.adjacencia.keySet()) {
            if (no.getNivel() == Nivel.NIVEL_MEIO_DE_TRANSPORTE) {
                grafoService.adicionarAresta(paciente, no, no.getTempo());
            }
            if (no.getNivel() == Nivel.NIVEL_UPA) {
                for (NoGrafo noDaVez : grafoService.adjacencia.keySet()) {
                    if (noDaVez.getNivel() == Nivel.NIVEL_MEIO_DE_TRANSPORTE) {
                        for (Par<String, Integer> tempoMeioDeTransporteUpa : valorArestaTransporteUpa.get(no.getNome())) {
                            if (tempoMeioDeTransporteUpa.getChave().equals(noDaVez.getNome())) {
                                grafoService.adicionarAresta(no, noDaVez, tempoMeioDeTransporteUpa.getValor());
                            }
                        }
                    }
                }
            }
            if (no.getNivel() == Nivel.NIVEL_TEMPO_DE_ESPERA) {
                for (NoGrafo noDaVez : grafoService.adjacencia.keySet()) {
                    if (noDaVez.getNivel() == Nivel.NIVEL_UPA) {
                        if (no.getNome().equals(noDaVez.getNome() + "-" + "tempoEspera")) {
                            listaUpas.add(noDaVez);
                            rotaMedicos.put(noDaVez, no);
                            grafoService.adicionarAresta(no, noDaVez, no.getTempo());
                        }
                    }
                }
            }
        }

    }

    public Map<NoGrafo, Double> build(){
        grafoService.limparDados();
        gerarNosGrafo();
        gerarArestasGrafo();
        return grafoService.algoritmoDijkstra();
    }

    public MelhorCaminho buildOtimizado(){
        grafoService.limparDados();
        gerarNosGrafo();
        gerarArestasGrafo();
        return grafoService.caminhoOtimizado(grafoService.algoritmoDijkstra(), listaUpas, rotaMedicos);
    }
}

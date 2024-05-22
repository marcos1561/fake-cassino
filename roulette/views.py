import traceback, locale
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse, Http404, JsonResponse

from .models import Beter
from .roulette.colors import ColorMapper
from .roulette.roulette import State, roletinha, LowMoneyError
from .user_info import cassino_info

from . import get_user_data
get_user_data.get_users_bets()


def index(request):
    user = {
        "is_authenticated": False,
        "username": None,
        "balance": None,
    }   
    
    if request.user.is_authenticated:
        user = {
            "is_authenticated": True,
            "username": request.user.username,
            "balance": request.user.beter.balance,
        }

    return render(request, "roulette/index.html", {"user": user})

def reset_balance(request):
    for beter in Beter.objects.all():
        beter.balance = 0

def check_auth(request):
    if request.user.is_authenticated:
        return HttpResponse(f"Sim: {request.user.username}")
    else:
        return HttpResponse("Nao")

status_str = {
    State.waiting: "Esperando apostas",
    State.rolling: "Rolando...",
    State.finished: "Finalizado",
}

state_id = {
    State.waiting: 0,
    State.rolling: 1,
    State.finished: 2,
}

def get_status(request):
    state = request.GET.get("state")
    if state == "":
        state = None
    else:
        state = int(state)

    user_roulette_state = {
        "num_bets": int(request.GET.get("num_bets")),
        "state": state,
    }

    first_request = user_roulette_state["state"] is None
    has_seen_new_roll = True

    status_content = None
    if user_roulette_state["state"] != state_id[roletinha.state] or first_request:
        state = roletinha.state
        if state in State.waiting | State.rolling:
            status_content = f'<div class="status">{status_str[state]}</div>'
        else:
            has_seen_new_roll = False
            color = ColorMapper.to_str(roletinha.color_rolled, lang="pt").capitalize()
            eng_color = ColorMapper.to_str(roletinha.color_rolled)
            status_content = f'<div class="status rolled_{eng_color}">{color}</div>'
    
    history_content = None
    balance_content = None
    if not has_seen_new_roll or first_request:
        history_content = ""
        for count, color_id in enumerate(roletinha.history.get(12 * 2)):
            if color_id == -1:
                continue
            color_str = ColorMapper.id_to_str(color_id)
            history_content += f'<div class="history_roll bg_{color_str}"> {count+1} º</div>\n'
        
        balance_content = locale.currency(roletinha.balance, grouping=True)
    
    bets_amount_content = None
    if user_roulette_state["num_bets"] != roletinha.num_bets or first_request:
        bets_amount_content = {ColorMapper.to_str(c): locale.currency(amount, grouping=True) for c, amount in roletinha.bets_amount.items()}
    
    color_rolled = None    
    if roletinha.has_rolled:
        color_rolled = ColorMapper.to_id(roletinha.color_rolled)

    cassino_p_gain = str(round(cassino_info.cassino_info["prob_gain"], 3)).replace(".", ",") + " %"

    return JsonResponse({
        "status": status_content,
        "bets_amount": bets_amount_content,
        "history": history_content,
        "balance": balance_content,
        "prob_gain": cassino_p_gain,
        "new_state": {"state": state_id[roletinha.state], "num_bets": roletinha.num_bets,
                      "color_rolled": color_rolled},
    })

def get_user_info(request, first_request=1):
    if not request.user.is_authenticated:
        return JsonResponse({
            "is_authenticated": False,
            "login_page": loader.render_to_string(
                "roulette/user_info.html", 
                {"is_authenticated": False}, request),
        })

    beter: Beter = request.user.beter

    if not beter.has_changed and first_request != 1:
        return JsonResponse({"to_update": False})
    
    beter.has_changed = False
    beter.save()

    # balance = f"{beter.balance} R$"
    # money_won = f"{beter.money_won} R$"
    # money_spend = f"{beter.money_spend} R$"
    # gain = f"{beter.gain} R$"
    balance = locale.currency(beter.balance, grouping=True)
    money_won = locale.currency(beter.money_won, grouping=True)
    money_spend = locale.currency(beter.money_spend, grouping=True)
    gain = locale.currency(beter.gain, grouping=True)
    num_bets = len(beter.bethistory_set.all())

    content = {
        "to_update": True,
        "is_authenticated": True,
        "balance": balance,
        "money_won": money_won,
        "money_spend": money_spend,
        "num_bets": num_bets,
        "gain": gain,
    }

    if first_request == 1:
        print("OPAPOAPA")
        content["user_page"] = loader.render_to_string("roulette/user_info.html",
            {"name": request.user.username, "is_authenticated": True}, request)

    return JsonResponse(content)

def get_wallet(request):
    if not request.user.is_authenticated:
        return HttpResponse()

    balance = request.user.beter.balance
    return HttpResponse(f"Carteira: {balance} R$")

def get_history(request, num):
    if num > 1000:
        raise Http404("Número máximo de histórico excedido.")
    
    return JsonResponse({"history": roletinha.history.get(num)})

def make_bet(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'User not authenticated'}, status=401)
    

    if request.method == 'POST':
        if roletinha.state is not State.waiting:
            return JsonResponse({'error': 'Roulette not waiting'}, status=403)

        try:
            color = request.POST['color']
            bet_amount = float(request.POST['amount'])
            # print(f"Color: {color}\nAmount: {bet_amount}")
        except Exception as e:
            traceback.print_exception(e)
            raise Http404("Erro extraindo as informações da aposta")

        # if bet_amount > request.user.beter.balance:
        #     return JsonResponse({'error': 'Not enough money'}, status=402)

        try:
            roletinha.register_bet(bet_amount, color, request.user.beter)
        except LowMoneyError as e:
            return JsonResponse({'error': 'Not enough money'}, status=402)
        except Exception as e:
            traceback.print_exception(e)
            raise Http404("Erro registrando a aposta")
        
        return HttpResponse()



def about(request):
    context = {"code_snippet": "def greet(name):\n    print('Hello, ' + name + '!')\n\ngreet('World')"}
    return render(request, "roulette/about.html", context)

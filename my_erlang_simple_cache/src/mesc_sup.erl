%% @author 重剑
%% @doc @todo Add description to mesc_sup.


-module(mesc_sup).
-behaviour(supervisor).
-export([start_link/0, start_child/2]).

%% ====================================================================
%% API functions
%% ====================================================================

-define(SERVER, ?MODULE).


%% ====================================================================
%% Behavioural functions
%% ====================================================================
-export([init/1]).


start_link() ->
    supervisor:start_link({local, ?SERVER}, ?MODULE, []).

start_child(Value, LeaseTime) ->
    supervisor:start_link(?SERVER, [Value, LeaseTime]).

%% init/1
%% ====================================================================
%% @doc <a href="http://www.erlang.org/doc/man/supervisor.html#Module:init-1">supervisor:init/1</a>
-spec init(Args :: term()) -> Result when
	Result :: {ok, {SupervisionPolicy, [ChildSpec]}} | ignore,
	SupervisionPolicy :: {RestartStrategy, MaxR :: non_neg_integer(), MaxT :: pos_integer()},
	RestartStrategy :: one_for_all
					 | one_for_one
					 | rest_for_one
					 | simple_one_for_one,
	ChildSpec :: {Id :: term(), StartFunc, RestartPolicy, Type :: worker | supervisor, Modules},
	StartFunc :: {M :: module(), F :: atom(), A :: [term()] | undefined},
	RestartPolicy :: permanent
				   | transient
				   | temporary,
	Modules :: [module()] | dynamic.
%% ====================================================================
init([]) ->
    Element = {mesc_element, {mesc_element, start_link, []},
                temporary, brutal_kill, worker, [mesc_element]},
    Children = [Element],
    RestartStrategy = {simple_one_for_one, 0, 1},
    {ok, {RestartStrategy, Children}}.

%% ====================================================================
%% Internal functions
%% ====================================================================



from services.action.playbooks.loader import PlaybookLoader

loader = PlaybookLoader()
playbooks = loader.load()

print(playbooks)
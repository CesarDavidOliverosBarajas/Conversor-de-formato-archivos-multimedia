from src.controller.app_controller import AppController
from src.view.main_window import MainWindow

def main():
    # Instanciar el controlador central
    controller = AppController()
    
    # Inyectar el controlador en la Vistas UX (Inversion of Control simple)
    app = MainWindow(controller)
    
    # Asignar referencia circular de vista hacia el controlador
    controller.view = app
    
    # Iniciar Mainloop de GUI
    app.mainloop()

if __name__ == "__main__":
    main()
